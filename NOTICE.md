# Licenças

- **Este repositório** (configs, `make-efi.py` e documentação) é uma versão modificada da EFI do
  [JulioNectar/Hackintosh-XPS13Plus-IrisXe-Tahoe](https://github.com/JulioNectar/Hackintosh-XPS13Plus-IrisXe-Tahoe)
  (commit `6b5f049`), adaptada ao Dell Vostro 3520 (as mudanças estão no [README](README.md)). Aquele projeto deriva do
  [NootedGreen](https://github.com/sgiammori/NootedGreen) de StezzaPilot, e este repositório é distribuído sob a mesma
  **Thou Shalt Not Profit License 1.0** ([LICENSE](LICENSE)): livre para usar, estudar, modificar e compartilhar, sem fins
  lucrativos.
- **`EFI/OC/Kexts/NootedGreen.kext`** é o binário daquele projeto no commit `6b5f049`, sem alterações (TSNPL 1.0). O
  código-fonte está em `src/NootedGreen` do mesmo repositório, nesse commit.
- **`EFI/OC/Kexts/RealtekRTL8111.kext`** é a release v3.0.0 de
  [Mieze/RTL8111_driver_for_OS_X](https://github.com/Mieze/RTL8111_driver_for_OS_X), sem alterações, sob a **GNU GPL
  v2 ou posterior** ([licenses/GPL-2.0.txt](licenses/GPL-2.0.txt)). Fonte: a tag `v3.0.0` desse repositório.
- **`EFI/OC/Kexts/HoRNDIS.kext`** é a release rel9.2 de [jwise/HoRNDIS](https://github.com/jwise/HoRNDIS) (extraída do
  `HoRNDIS-9.2.pkg`), sem alterações, sob a **GNU GPL v3** ([licenses/GPL-3.0.txt](licenses/GPL-3.0.txt)). Fonte: a tag
  `rel9.2` desse repositório.
- **`EFI/OC/Kexts/UTBMap.kext`** é o mapa USB deste notebook para o USBToolBox, feito para este repositório.
- **Os demais componentes de `EFI/`** vêm sem alterações do projeto original e mantêm as próprias licenças: OpenCore,
  Lilu, WhateverGreen, VirtualSMC e plugins SMC, NVMeFix, RestrictEvents, BrightnessKeys, CpuTopologyRebuild (acidanthera
  e colaboradores); VoodooI2C e VoodooPS2 (seus autores); USBToolBox (dhinakg); XHCI-unsupported (RehabMan, GPLv2).
- **Nenhum software da Apple está incluído.** `HfsPlus.efi` e o recovery do macOS são baixados pelo `make-efi.py` na
  sua máquina. Apple, macOS e Metal são marcas da Apple Inc. Este projeto não tem relação com a Apple, a Intel ou a Dell.
