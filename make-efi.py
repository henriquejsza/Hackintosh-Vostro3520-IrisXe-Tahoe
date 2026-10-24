#!/usr/bin/env python3
"""Monta dist/EFI, pronta para o pendrive, a partir da pasta EFI/ deste repositório (Linux ou macOS).

    python3 make-efi.py               dist/EFI com o SMBIOS do smbios.local (gera um novo se ele não existir)
    python3 make-efi.py --recovery    também baixa o recovery do macOS Tahoe para dist/com.apple.recovery.boot

O git não guarda três coisas, e este script as repõe:
  - os números de série (SMBIOS MacBookPro16,2): ficam no smbios.local, fora do git. Guarde esse arquivo:
    números novos fazem o iCloud/iMessage ver outro Mac.
  - HfsPlus.efi (binário da Apple): baixado do acidanthera/OcBinaryData e conferido por SHA-256.
  - o recovery do macOS (da Apple): baixado dos servidores da Apple pelo macrecovery do OpenCore.
"""
import argparse
import hashlib
import os
import platform
import plistlib
import secrets
import shutil
import subprocess
import sys
import uuid
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
DEPS = os.path.join(ROOT, 'build', 'deps')
DIST = os.path.join(ROOT, 'dist')
SMBIOS = os.path.join(ROOT, 'smbios.local')
CONFIGS = ('config.plist', 'config-install.plist', 'config-accel.plist')
MODEL = 'MacBookPro16,2'
BOARD = 'Mac-5F9802EFE386AA28'  # board-id do MacBookPro16,2, usado pelo macrecovery
OC_VER = '1.0.8'
OC_ZIP = (f'https://github.com/acidanthera/OpenCorePkg/releases/download/{OC_VER}/OpenCore-{OC_VER}-RELEASE.zip',
          '2011e8b7216ecb2645d97ea710df965947edd406846e92050b9bc4190be6d27b')
HFSPLUS = ('https://raw.githubusercontent.com/acidanthera/OcBinaryData/'
           'c2a98980d30e39a571a2843ab26aa8d2b9188094/Drivers/HfsPlus.efi',
           'a55b5fff36578864ba6792c4c6369c71f6f35b61dd5a853ddf8583cd36c31d8f')
KEYS = ('SystemSerialNumber', 'MLB', 'SystemUUID', 'ROM')


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def fetch(url, digest, dest):
    """Baixa url para dest (com cache) e confere o SHA-256."""
    if os.path.exists(dest) and sha256(dest) == digest:
        return dest
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    print(f'  baixando {os.path.basename(dest)}')
    tmp = dest + '.part'
    try:
        subprocess.run(['curl', '-fL', '--retry', '3', '-sS', '-o', tmp, url], check=True)
    except subprocess.CalledProcessError:
        sys.exit(f'erro: não consegui baixar {url}')
    if sha256(tmp) != digest:
        os.remove(tmp)
        sys.exit(f'erro: SHA-256 inesperado em {url}')
    os.replace(tmp, dest)
    return dest


def oc_utilities():
    """Utilitários do OpenCore (macserial, ocvalidate, macrecovery) da release oficial."""
    base = os.path.join(DEPS, f'OpenCore-{OC_VER}')
    if not os.path.isdir(os.path.join(base, 'Utilities', 'macrecovery')):
        z = fetch(*OC_ZIP, os.path.join(DEPS, f'OpenCore-{OC_VER}-RELEASE.zip'))
        with zipfile.ZipFile(z) as zf:
            for name in zf.namelist():
                if name.startswith(('Utilities/macserial/', 'Utilities/ocvalidate/', 'Utilities/macrecovery/')):
                    zf.extract(name, base)
    return os.path.join(base, 'Utilities')


def oc_tool(name):
    suffix = {'Linux': '.linux', 'Darwin': ''}.get(platform.system())
    if suffix is None:
        sys.exit('erro: rode no Linux ou no macOS')
    path = os.path.join(oc_utilities(), name, name + suffix)
    os.chmod(path, 0o755)  # o zipfile não preserva o bit de execução
    return path


def load_smbios():
    """Lê o smbios.local; se ele não existir, gera um SMBIOS novo com o macserial e o salva."""
    if os.path.exists(SMBIOS):
        vals = {}
        with open(SMBIOS, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    vals[key.strip()] = value.strip()
        missing = [k for k in KEYS if not vals.get(k)]
        if missing:
            sys.exit(f'erro: smbios.local sem {", ".join(missing)}')
        try:
            vals['ROM'] = bytes.fromhex(vals['ROM'])
        except ValueError:
            sys.exit('erro: ROM no smbios.local deve ter 12 dígitos hexadecimais')
        if len(vals['ROM']) != 6:
            sys.exit('erro: ROM no smbios.local deve ter 12 dígitos hexadecimais')
        vals['SystemProductName'] = vals.get('SystemProductName') or MODEL
        print('  SMBIOS: smbios.local')
        return vals

    out = subprocess.check_output([oc_tool('macserial'), '-m', MODEL, '-g', '-n', '1'], text=True)
    serial, mlb = (x.strip() for x in out.strip().splitlines()[0].split('|'))
    vals = {'SystemProductName': MODEL, 'SystemSerialNumber': serial, 'MLB': mlb,
            'SystemUUID': str(uuid.uuid4()).upper(), 'ROM': secrets.token_bytes(6)}
    fd = os.open(SMBIOS, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(f'# SMBIOS desta máquina ({MODEL}). Não publique e não apague:\n'
                '# números novos fazem o iCloud/iMessage ver outro Mac.\n')
        for key in ('SystemProductName',) + KEYS:
            value = vals[key].hex() if key == 'ROM' else vals[key]
            f.write(f'{key}={value}\n')
    print('  SMBIOS: novo, salvo em smbios.local (guarde esse arquivo)')
    return vals


def build_efi(vals):
    efi = os.path.join(DIST, 'EFI')
    if os.path.exists(efi):
        shutil.rmtree(efi)
    shutil.copytree(os.path.join(ROOT, 'EFI'), efi)
    shutil.copy(fetch(*HFSPLUS, os.path.join(DEPS, 'HfsPlus.efi')), os.path.join(efi, 'OC', 'Drivers', 'HfsPlus.efi'))
    ocvalidate = oc_tool('ocvalidate')
    for name in CONFIGS:
        path = os.path.join(efi, 'OC', name)
        with open(path, 'rb') as f:
            config = plistlib.load(f)
        config['PlatformInfo']['Generic'].update(
            {k: vals[k] for k in ('SystemProductName',) + KEYS})
        with open(path, 'wb') as f:
            plistlib.dump(config, f)
        result = subprocess.run([ocvalidate, path], capture_output=True, text=True)
        if result.returncode != 0 or 'No issues found' not in result.stdout:
            sys.exit(f'erro: ocvalidate reprovou {name}:\n{result.stdout}{result.stderr}')
        print(f'  {name}: ocvalidate OK')
    return efi


def download_recovery():
    out = os.path.join(DIST, 'com.apple.recovery.boot')
    if os.path.exists(os.path.join(out, 'BaseSystem.dmg')):
        print('  recovery: já existe em dist/com.apple.recovery.boot (apague a pasta para baixar de novo)')
        return out
    # baixa numa pasta temporária: o macrecovery confere a imagem com o chunklist e sai com erro se ela não bater,
    # então só uma imagem completa vira dist/com.apple.recovery.boot
    part = os.path.join(DIST, 'recovery.part')
    if os.path.exists(part):
        shutil.rmtree(part)
    macrecovery = os.path.join(oc_utilities(), 'macrecovery')
    try:
        subprocess.run([sys.executable, 'macrecovery.py', '-b', BOARD, '-m', '00000000000000000', '-os', 'latest',
                        '-o', part, 'download'], check=True, cwd=macrecovery)
    except subprocess.CalledProcessError:
        sys.exit('erro: o download do recovery falhou; rode de novo')
    os.replace(part, out)
    return out


def main():
    parser = argparse.ArgumentParser(description='Monta dist/EFI para o Dell Vostro 3520.')
    parser.add_argument('--recovery', action='store_true', help='baixa também o recovery do macOS Tahoe (~1 GB)')
    args = parser.parse_args()

    print('== EFI')
    efi = build_efi(load_smbios())
    recovery = None
    if args.recovery:
        print('== recovery do macOS')
        recovery = download_recovery()

    print(f'\nPronto: {os.path.relpath(efi, ROOT)}' + (f' e {os.path.relpath(recovery, ROOT)}' if recovery else ''))
    print('Copie para a raiz de uma partição FAT32 do pendrive. A config.plist é a SEGURA (sem aceleração).')
    print('Não publique dist/ nem o smbios.local: eles têm os seus números de série.')


if __name__ == '__main__':
    main()
