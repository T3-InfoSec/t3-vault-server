import argparse
from ssl import CERT_REQUIRED
import uvicorn
from fastapi import FastAPI
from app.database.database import Base, engine
from app.services import connection_manager
from app.sokcets_handlers import client_ws, solver_ws
from app.database.events import init_events
from loguru import logger

from trustme_issuers import (
    CertificateType,
    CryptoCoordinator,
    CryptoDumper,
    PrimitivePaths,
)

root_ca = CryptoCoordinator(
    certificate_name="Emulated Root", certificate_type=CertificateType.ROOT
)
public_ca = CryptoCoordinator(
    certificate_name="Emulated Public CA",
    certificate_type=CertificateType.INTERMEDIATE,
    certificate_signer=root_ca.certificate_signer,
)
private_ca = CryptoCoordinator(
    certificate_name="Emulated Private CA",
    certificate_type=CertificateType.INTERMEDIATE,
    certificate_signer=root_ca.certificate_signer,
)

client_certificate = CryptoCoordinator(
    certificate_name="Client",
    certificate_type=CertificateType.LEAF,
    certificate_signer=private_ca.certificate_signer,
)

server_certificate = CryptoCoordinator(
    certificate_name="Server",
    certificate_type=CertificateType.LEAF,
    certificate_signer=public_ca.certificate_signer,
)

CryptoDumper.dump_full_chain(
    leaf=client_certificate, intermediates=[private_ca, public_ca], root=root_ca
)
CryptoDumper.dump_full_chain(
    leaf=server_certificate, intermediates=[public_ca], root=root_ca
)
CryptoDumper.dump_full_chain(intermediates=[private_ca], root=root_ca)

CryptoDumper.dump_pfx(leaf=client_certificate)


app = FastAPI()


# Create database tables
Base.metadata.create_all(bind=engine)

init_events()


@app.get("/")
def hello():
    return {"message": "Hello World"}

# Register WebSocket routes
app.add_api_websocket_route("/ws/client/{client_id}", client_ws.client_websocket)
app.add_api_websocket_route("/ws/solver/{solver_id}", solver_ws.solver_websocket)


def hints(openssl_hints: bool):
    logger.warning(
        f"""\n You will need to install root certificate and Client Certificate Bundle. Run: 
        \n ⌨️  Get-ChildItem -Path '{root_ca.storage_path/PrimitivePaths.CERTIFICATE}' | Import-Certificate -CertStoreLocation cert:\CurrentUser\Root 
        \n ⌨️  Get-ChildItem -Path '{client_certificate.storage_path/PrimitivePaths.PFX}' | Import-PfxCertificate -CertStoreLocation Cert:\CurrentUser\My 
        \n 🍎 security import '{root_ca.storage_path/PrimitivePaths.CERTIFICATE}' -k ~/Library/Keychains/login.keychain        
        """
    )
    if openssl_hints:
        logger.info(
            f"""\n Test Valid Client Cert with OpenSSL
            \n openssl s_client -connect 127.0.0.1:5000 -cert '{client_certificate.storage_path/PrimitivePaths.CERTIFICATE}' -key '{client_certificate.storage_path/PrimitivePaths.PRIVATE_KEY}'"""
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run a FastAPI Server with mTLS Support"
    )
    parser.add_argument(
        "--openssl-hints",
        action="store_true",
        help="Output OpenSSL s_client commands",
    )
    args = parser.parse_args()
    hints(openssl_hints=args.openssl_hints)
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="trace",
        ssl_keyfile=str(server_certificate.storage_path / PrimitivePaths.PRIVATE_KEY),
        ssl_certfile=str(server_certificate.storage_path / PrimitivePaths.FULLCHAIN),
        ssl_cert_reqs=CERT_REQUIRED,        
        ssl_ca_certs=str(private_ca.storage_path / PrimitivePaths.FULLCHAIN),
    )
