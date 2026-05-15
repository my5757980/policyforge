from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from app.models.policy import Policy, PolicyCreate, PolicyResponse
from app.services import gemini_service, lobster_service

router = APIRouter(prefix="/api/policies", tags=["policies"])


@router.post("/generate")
async def generate_policy(req: PolicyCreate):
    try:
        yaml_content, name = await gemini_service.generate_policy_yaml(req.description)
        return {"yaml": yaml_content, "name": name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini error: {str(e)}")


@router.post("/activate")
async def activate_policy(req: PolicyCreate, yaml_content: str, name: str, session: Session = Depends(get_session)):
    policy = Policy(
        name=name,
        description=req.description,
        yaml_content=yaml_content,
        is_active=True,
        compliance_tags=",".join(req.compliance_tags),
    )
    session.add(policy)
    session.commit()
    session.refresh(policy)
    lobster_service.write_policy_yaml(policy.id, yaml_content)
    return _to_response(policy)


@router.post("/save")
async def save_policy(body: dict, session: Session = Depends(get_session)):
    policy = Policy(
        name=body.get("name", "unnamed-policy"),
        description=body.get("description", ""),
        yaml_content=body.get("yaml_content", ""),
        is_active=True,
        compliance_tags=",".join(body.get("compliance_tags", [])),
    )
    session.add(policy)
    session.commit()
    session.refresh(policy)
    lobster_service.write_policy_yaml(policy.id, policy.yaml_content)
    return _to_response(policy)


@router.get("")
def list_policies(session: Session = Depends(get_session)):
    policies = session.exec(select(Policy)).all()
    return [_to_response(p) for p in policies]


@router.delete("/{policy_id}")
def delete_policy(policy_id: str, session: Session = Depends(get_session)):
    policy = session.get(Policy, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    policy.is_active = False
    session.add(policy)
    session.commit()
    lobster_service.remove_policy_yaml(policy_id)
    return {"ok": True}


def _to_response(p: Policy) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "yaml_content": p.yaml_content,
        "is_active": p.is_active,
        "compliance_tags": [t for t in p.compliance_tags.split(",") if t],
        "created_at": p.created_at.isoformat(),
    }
