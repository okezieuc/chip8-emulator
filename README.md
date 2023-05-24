# CHIP-8 Emulator in Python

This is an emulator of the CHIP-8 interpreter written in Python. The emulator allows you to run CHIP-8 ROMs on your computer, providing an opportunity to explore and understand low-level concepts in computer architecture.

## Usage Guide

To use this CHIP-8 emulator:

1. Download a ROM file. You can find CHIP-8 ROMS at the following locations
    - http://devernay.free.fr/hacks/chip8/GAMES.zip 
    - https://github.com/kripod/chip8-roms

2. Move the ROM into the root directory of this project.

3. Start the emulator with the following command.

```bash
python index.py <ROM_NAME>
```

Replace `ROM_NAME` with the name of the ROM file you wish to run.

4. During runtime, the emulator window will display the CHIP-8 screen, and you can interact with the game using the following keyboard mappings:

    ```
    1234
    QWER
    ASDF
    ZXCV
    ```

## Instruction Validity Tester

To validate the implementation of CHIP-8 instructions in this emulator you can use a CHIP-8 validator rom.

1. Download the [CHIP-8 validity tester ROM](https://github.com/corax89/chip8-test-rom)

2. Move the validity tester ROM into the root directory

3. Run the emulator with the following command:

```bash
python index.py test_opcode.ch8
```

## Known Limitations
- The implementation of the sound timer is incomplete.

## Credits

- [Emulation Basics: Write your own CHIP-8 Emulator/Interpreter](https://omokute.blogspot.com/2012/06/emulation-basics-write-your-own-chip-8.html)
- [Cowgod's Chip-8 Technical Reference](http://devernay.free.fr/hacks/chip8/C8TECH10.HTM#0.0)
- [CHIP-8 Games](http://devernay.free.fr/hacks/chip8/GAMES.zip)
