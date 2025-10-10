#!/usr/bin/env python3
"""
Generate RSA key pair for license signing.
This script generates the private key for signing licenses and the public key for verification.
"""
import click
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


@click.command()
@click.option('--key-size', default=2048, help='RSA key size in bits (default: 2048)')
@click.option('--private-key-file', default='license_private_key.pem', help='Private key output file')
@click.option('--public-key-file', default='license_public_key.pem', help='Public key output file')
@click.option('--force', is_flag=True, help='Overwrite existing key files')
def generate_keys(key_size: int, private_key_file: str, public_key_file: str, force: bool):
    """Generate RSA key pair for license signing."""
    
    private_path = Path(private_key_file)
    public_path = Path(public_key_file)
    
    # Check if files already exist
    if (private_path.exists() or public_path.exists()) and not force:
        click.echo("Error: Key files already exist. Use --force to overwrite.")
        click.echo(f"Private key: {private_path.absolute()}")
        click.echo(f"Public key: {public_path.absolute()}")
        return
    
    click.echo(f"Generating {key_size}-bit RSA key pair...")
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )
    
    # Get public key
    public_key = private_key.public_key()
    
    # Serialize private key (no password for simplicity)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Serialize public key
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    # Write private key
    with open(private_path, 'wb') as f:
        f.write(private_pem)
    
    # Write public key
    with open(public_path, 'wb') as f:
        f.write(public_pem)
    
    # Set secure permissions on private key
    private_path.chmod(0o600)
    
    click.echo("✅ RSA key pair generated successfully!")
    click.echo(f"🔐 Private key: {private_path.absolute()} (keep secure!)")
    click.echo(f"🔓 Public key: {public_path.absolute()}")
    click.echo()
    click.echo("📋 Next steps:")
    click.echo("1. Keep the private key secure - it's used to sign licenses")
    click.echo("2. The public key will be embedded in the application")
    click.echo("3. Update the license generator to use the private key")
    click.echo("4. Update the license manager to use the public key")
    click.echo()
    click.echo("⚠️  SECURITY WARNING:")
    click.echo("   - Store the private key securely (not in version control)")
    click.echo("   - If the private key is compromised, all licenses can be forged")
    click.echo("   - Consider using hardware security modules for production")


if __name__ == '__main__':
    generate_keys()