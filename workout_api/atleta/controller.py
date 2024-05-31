from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, status, Body, HTTPException
from pydantic import UUID4
from sqlalchemy import select

from workout_api import CentroTreinamentoModel
from workout_api.categorias.models import CategoriaModel
from workout_api.atleta.models import AtletaModel
from workout_api.atleta.schemas import AtletaIn, AtletaOut, AtletaUpdate
from workout_api.contrib.dependencies import DatabaseDependency

router = APIRouter()


@router.post(
    '/',
    summary='Criar novo atleta',
    status_code=status.HTTP_201_CREATED,
    response_model=AtletaOut
)
async def post(
        db_session: DatabaseDependency,
        atleta_in: AtletaIn = Body(...)
):
    nome_categoria = atleta_in.categoria.nome
    comando = select(CategoriaModel).filter_by(nome=nome_categoria)
    categoria = (await db_session.execute(comando)).scalars().first()
    if not categoria:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Categoria {nome_categoria} nao encontrada')

    nome_ct = atleta_in.centro_treinamento.nome
    comando = select(CentroTreinamentoModel).filter_by(nome=nome_ct)
    centro_treinamento = (await db_session.execute(comando)).scalars().first()
    if not centro_treinamento:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Centro de treinamento {centro_treinamento} nao encontrado')

    try:
        atleta_out = AtletaOut(id=uuid4(), created_at=datetime.utcnow(), **atleta_in.model_dump())
        atleta_model = AtletaModel(**atleta_out.model_dump(exclude={'categoria', 'centro_treinamento'}))
        atleta_model.categoria_id = categoria.pk_id
        atleta_model.centro_treinamento_id = centro_treinamento.pk_id

        db_session.add(atleta_model)
        await db_session.commit()
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'Ocorreu um erro ao inserir os dados no BD')

    return atleta_out

@router.get(
    '/',
    summary='Consultar todas os atletas',
    status_code=status.HTTP_200_OK,
    response_model=list[AtletaOut],
)
async def query(db_session: DatabaseDependency) -> list[AtletaOut]:
    comando = select(AtletaModel)
    atletas: list[AtletaOut] = (await db_session.execute(comando)).scalars().all()
    return [AtletaOut.model_validate(atleta) for atleta in atletas]


@router.get(
    '/{id}',
    summary='Consultar um atleta pelo id',
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def query(id: UUID4, db_session: DatabaseDependency) -> AtletaOut:
    comando = select(AtletaModel).filter_by(id=id)
    atleta: AtletaOut = (await db_session.execute(comando)).scalars().first()

    if not atleta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Atleta nao encontrado para o id {id}')
    return atleta


@router.patch(
    '/{id}',
    summary='Editar um atleta pelo id',
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def query(id: UUID4, db_session: DatabaseDependency,
                atleta_up: AtletaUpdate = Body(...)) -> AtletaOut:
    comando = select(AtletaModel).filter_by(id=id)
    atleta: AtletaOut = (await db_session.execute(comando)).scalars().first()

    if not atleta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Atleta nao encontrado para o id {id}')

    atleta_update = atleta_up.model_dump(exclude_unset=True)

    for key, value in atleta_update.items():
        setattr(atleta, key, value)

    await db_session.commit()
    await db_session.refresh(atleta)

    return atleta


@router.delete(
    '/{id}',
    summary='Deletar um atleta pelo id',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def query(id: UUID4, db_session: DatabaseDependency) -> None:
    comando = select(AtletaModel).filter_by(id=id)
    atleta: AtletaOut = (await db_session.execute(comando)).scalars().first()

    if not atleta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Atleta nao encontrado para o id {id}')

    await db_session.delete(atleta)
    await db_session.commit()

