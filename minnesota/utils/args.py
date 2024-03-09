"""Args utils"""

from os import environ, getcwd
from argparse import ArgumentParser
from pathlib import Path


def get_args() -> (  # noqa: C901, PLR0915 # pylint: disable=too-many-locals
    tuple[list[Path], Path, str, int, bool]
):  # pragma: no cover
    """Get args"""
    parser: ArgumentParser = ArgumentParser(prog="minnesota")
    parser.add_argument(
        "--routes-folder",
        type=str,
        required=True,
        nargs="+",
        help="Folders with routes",
        dest="routes_folder",
    )
    parser.add_argument(
        "-e",
        "--env",
        action="append",
        required=False,
        help="Environment variables",
        dest="env",
        type=str,
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        required=False,
        help="Port to listen on",
        dest="port",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",  # nosec
        required=False,
        help="Host to listen on",
        dest="host",
    )
    parser.add_argument(
        "--cwd",
        type=str,
        default=getcwd(),
        required=False,
        help="Current working directory",
        dest="cwd",
    )
    parser.add_argument(
        "--sub",
        type=str,
        required=False,
        default=None,
        help="Cognito sub for debug",
        dest="sub",
    )
    parser.add_argument(
        "--email",
        type=str,
        required=False,
        default=None,
        help="Cognito email for debug",
        dest="email",
    )
    parser.add_argument(
        "--stripe-key",
        type=str,
        required=False,
        default=None,
        help="Stripe api key",
        dest="stripe_key",
    )
    parser.add_argument(
        "--stripe-plans",
        type=str,
        required=False,
        default=None,
        help="Stripe advanced plans",
        dest="stripe_plans",
    )
    parser.add_argument(
        "--stripe-endpoint",
        type=str,
        required=False,
        default=None,
        help="Stripe endpoint",
        dest="stripe_endpoint",
    )
    parser.add_argument(
        "--aws-endpoint",
        type=str,
        required=False,
        default=None,
        help="AWS endpoint",
        dest="aws_endpoint",
    )
    parser.add_argument(
        "--mock",
        required=False,
        default=False,
        action="store_true",
        dest="mock",
        help="Launch as mock server (available only in debug mode)",
    )
    parser.add_argument(
        "--skip-stripe",
        required=False,
        default=False,
        action="store_true",
        dest="skip_stripe",
        help="Skip stripe check (available only in debug mode)",
    )
    parser.add_argument(
        "--secrets",
        type=str,
        required=False,
        default=None,
        help="Secretsmanager name",
        dest="secrets",
    )
    parser.add_argument(
        "--allowed-origins",
        type=str,
        required=False,
        default=None,
        help="Allowed CORS origins",
        dest="origins",
    )
    args = parser.parse_args()
    cwd: Path = Path(args.cwd)
    port: int = args.port
    host: str = args.host
    sub: str | None = args.sub
    email: str | None = args.email
    stripe_key: str | None = args.stripe_key
    stripe_plans: str | None = args.stripe_plans
    is_mock: bool = args.mock
    skip_stripe: bool = args.skip_stripe
    stripe_endpoint: str | None = args.stripe_endpoint
    aws_endpoint: str | None = args.aws_endpoint
    allowed_origins: str | None = args.origins
    secrets: str | None = args.secrets
    routes: list[Path] = [Path(fld) for fld in args.routes_folder]
    if allowed_origins:
        environ["ALLOWED_ORIGINS"] = allowed_origins
    if aws_endpoint:
        environ["AWS_ENDPOINT"] = aws_endpoint
    if args.env:
        envs: list[str] = args.env
        for env in envs:
            k, v = env.split("=")
            environ[k] = v
    if stripe_key:
        environ["STRIPE_API_KEY"] = stripe_key
    if stripe_plans:
        environ["ADVANCED_PLANS"] = stripe_plans
    if __debug__ and skip_stripe:
        environ["SKIP_STRIPE"] = "true"
    if __debug__ and stripe_endpoint:
        environ["STRIPE_ENDPOINT_URL"] = stripe_endpoint
    if secrets:
        environ["SECRET_NAME"] = secrets
    if sub is not None and __debug__:
        environ["FIXED_USER"] = sub
    if email is not None and __debug__:
        environ["FIXED_EMAIL"] = email
    if is_mock and __debug__:
        environ["IS_TEST"] = "true"
        environ["DEFAULT_REGION"] = "eu-west-1"
        environ["AWS_DEFAULT_REGION"] = "eu-west-1"
        environ["AWS_REGION"] = "eu-west-1"
        environ["STRIPE_ENDPOINT_URL"] = stripe_endpoint or "http://localhost:12111"
        environ["STRIPE_API_KEY"] = "sk_test_12345"
        environ["ADVANCED_PLANS"] = "prod_PEHTfnvdJH6K0k"
    return routes, cwd, host, port, is_mock


__all__ = ["get_args"]
