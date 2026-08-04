from dependency_injector import containers, providers

from src.application.use_cases.create_campaign_usecase import CreateCampanhaUseCase
from src.application.use_cases.dashboard_usecase import DashboardUseCase
from src.application.use_cases.local_usecase import LocalUseCase
from src.application.use_cases.team_usecase import TimeUseCase
from src.application.use_cases.update_campaign_usecase import UpdateCampaignUseCase
from src.application.use_cases.user_usecase import UserUseCase
from src.application.use_cases.venda_usecase import VendaUseCase
from src.infra.database.session import SessionLocal
from src.infra.repositories.campaign_repository import CampanhaRepository
from src.infra.repositories.carteira_financeira import CarteiraFinanceiraRepository
from src.infra.repositories.local_repository import LocalRepository
from src.infra.repositories.TimeRepository import TimeRepository
from src.infra.repositories.user_repository import UserRepository
from src.infra.repositories.venda_repository import VendaRepository


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.infra.router.endpoint.user_route",
            "src.infra.router.endpoint.venda_route",
            "src.application.auth.auth",
            "src.infra.router.endpoint.campaign_route",
            "src.infra.router.endpoint.team_route",
            "src.infra.router.endpoint.local_route",
        ]
    )

    # Each resolution gets its own Session (see session.py for why this
    # can't safely be a shared/request-scoped Session in this stack).
    # Repositories close their session right after committing.
    db_session = providers.Factory(SessionLocal)

    user_repository = providers.Factory(
        UserRepository,
        db=db_session,
    )

    venda_repository = providers.Factory(
        VendaRepository,
        db=db_session,
    )

    campanha_repository = providers.Factory(CampanhaRepository, db=db_session)

    time_repository = providers.Factory(TimeRepository, db_session=db_session)
    carteira_repository = providers.Factory(CarteiraFinanceiraRepository, session=db_session)
    local_repository = providers.Factory(LocalRepository, db=db_session)

    user_usecase = providers.Factory(
        UserUseCase,
        user_repo=user_repository,
        time_repo=time_repository,
    )

    venda_usecase = providers.Factory(
        VendaUseCase,
        repository=venda_repository,
    )

    create_campaign_use_case = providers.Factory(
        CreateCampanhaUseCase, campanha_repo=campanha_repository, user_repo=user_repository
    )

    update_campaign_use_case = providers.Factory(
        UpdateCampaignUseCase,
        campanha_repo=campanha_repository,
        user_repo=user_repository,
    )

    time_usecase = providers.Factory(
        TimeUseCase,
        time_repository=time_repository,
    )
    local_usecase = providers.Factory(
        LocalUseCase,
        local_repository=local_repository,
    )
    dashboard_usecase = providers.Factory(
        DashboardUseCase,
        campanha_repo=campanha_repository,
        venda_repo=venda_repository,
        user_repo=user_repository,
        # time_repo=time_repository,
    )