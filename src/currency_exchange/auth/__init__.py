from currency_exchange.db.session import async_session_factory
from .repos import RepositoryABC, UsersRepository, TokenStateRepository
from .providers import verify_access, get_user_from_bearer_token


RepoType = RepositoryABC
RepoClsType = type[RepoType]

_repository_singletones = {}

def _get_repo(repo_type: type[RepoType]) -> RepoType:
    repo = _repository_singletones.get(repo_type)
    if repo is None:
        repo = repo_type(async_session_factory)
        _repository_singletones[repo_type] = repo
    return repo

def get_users_repo() -> UsersRepository:
    return _get_repo(UsersRepository)

def get_token_state_repo() -> TokenStateRepository:
    return _get_repo(TokenStateRepository)


