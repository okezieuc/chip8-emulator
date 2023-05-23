import pyglet
import sys
import random

class cpu(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pixel = pyglet.sprite.Sprite(pyglet.image.SolidColorImagePattern(color=(255, 255, 255, 255)).create_image(10, 10))

    def main(self):
        self.initialize()
        self.load_rom(sys.argv[1])
        while not self.has_exit:
            self.dispatch_events()
            self.cycle()
            self.draw()

    def initialize(self):
        self.clear()
        self.memory = [0] * 4096
        self.gpio = [0] * 16  # the registers
        self.display_buffer = [0] * 64 * 32
        self.stack = []
        self.key_inputs = [0] * 16
        self.opcode = 0
        self.index = 0

        self.delay_timer = 0
        self.sound_timer = 0
        self.should_draw = False
        self.key_wait = False

        self.pc = 0x200

        self.fonts = [0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
           0x20, 0x60, 0x20, 0x20, 0x70, # 1
           0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
           0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
           0x90, 0x90, 0xF0, 0x10, 0x10, # 4
           0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
           0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
           0xF0, 0x10, 0x20, 0x40, 0x40, # 7
           0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
           0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
           0xF0, 0x90, 0xF0, 0x90, 0x90, # A
           0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
           0xF0, 0x80, 0x80, 0x80, 0xF0, # C
           0xE0, 0x90, 0x90, 0x90, 0xE0, # D
           0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
           0xF0, 0x80, 0xF0, 0x80, 0x80  # F
           ]

        self.funcmap = {
            0x0000: self._0ZZZ,
            0x00e0: self._0ZZ0,
            0x00ee: self._0ZZE,
            0x1000: self._1ZZZ,
            0x2000: self._2ZZZ,
            0x3000: self._3ZZZ,
            0x4000: self._4ZZZ,
            0x5000: self._5ZZZ,
            0x6000: self._6ZZZ,
            0x7000: self._7ZZZ,
            0x8000: self._8ZZZ,
            0x8002: self._8ZZ2,
            0x8004: self._8ZZ4,
            0x8005: self._8ZZ5,
            0x8006: self._8ZZ6,
            0x800E: self._8ZZE,
            0x9000: self._9ZZ0,
            0xa000: self._AZZZ,
            0xc000: self._CZZZ,
            0xd000: self._DZZZ,
            0xe000: self._EZZZ,
            0xe09e: self._EZZE,
            0xe0a1: self._EZZ1,
            0xf000: self._FZZZ,
            0xf007: self._FZ07,
            0xf00a: self._FZ0A,
            0xf015: self._FZ15,
            0xf018: self._FZ18,
            0xf01e: self._FZ1E,
            0xf029: self._FZ29,
            0xf033: self._FZ33,
            0xf055: self._FZ55,
            0xf065: self._FZ65,
        }

        i = 0
        while i < 80:
            # load 80-char font set
            self.memory[i] = self.fonts[i]
            i += 1
    
    def load_rom(self, rom_path):
        log("Loading %s..." % rom_path)
        binary = open(rom_path, "rb").read()
        i = 0
        while i < len(binary):
            self.memory[i+0x200] = binary[i]
            i+=1

    def cycle(self):
        if not self.key_wait:
            self.opcode = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]  # Combine two bytes into a 16-bit opcode

            self.vx = (self.opcode & 0x0f00) >> 8
            self.vy = (self.opcode & 0x00f0) >> 4
            
            self.pc += 2

            extracted_op = self.opcode & 0xf000
            try:
                self.funcmap[extracted_op]()
            except:
                print("Unknown instruction: %X" % self.opcode)

            # decrement timers
            if self.delay_timer > 0:
                self.delay_timer -= 1
            if self.sound_timer > 0:
                self.sound_timer -= 1
                if self.sound_timer == 0:
                    # Play a sound here with pyglet!
                    pass

    def _0ZZZ(self):
        extracted_op = self.opcode & 0xf0ff
        try:
            self.funcmap[extracted_op]()
        except:
            print("Unknown instruction: %X" % self.opcode)

    def _0ZZ0(self):
        log("Clears the screen")
        self.display_buffer = [0]*64*32
        self.should_draw = True

    def _0ZZE(self):
        log("Returns from subroutine")
        self.pc = self.stack.pop()

    def _1ZZZ(self):
        log("Jumps to address NNN.")
        self.pc = self.opcode & 0x0fff

    def _2ZZZ(self):
        log("Call subroutine at NNN.")
        self.stack.append(self.pc)
        subroutine = self.opcode & 0x0fff
        self.pc = subroutine

    def _3ZZZ(self):
        log("Skip next instruction if Vx = kk")
        if self.gpio[self.vx] == (self.opcode & 0x00ff):
            self.pc += 2

    def _4ZZZ(self):
        log("Skip next instruction if Vx doesn't equal NN")
        if(self.gpio[self.vx] != (self.opcode & 0x00ff)):
            self.pc += 2
    
    def _5ZZZ(self):
        log("Skip next instruction if Vx = Vy")
        if(self.gpio[self.vx] == self.gpio[self.vy]):
            self.pc += 2

    def _6ZZZ(self):
        log("Set Vx = kk")
        self.gpio[self.vx] = (self.opcode & 0x00ff)

    def _7ZZZ(self):
        log("Set Vx to be Vx + kk")
        self.gpio[self.vx] = self.gpio[self.vx] + (self.opcode & 0x00ff)
    
    def _8ZZZ(self):
        extracted_op = self.opcode & 0xf00f
        if extracted_op == 0x8000:
            # run 8xy0 instruction
            log("Set Vx = Vy")
            self.gpio[self.vx] = self.gpio[self.vy]
            pass
        else:
            try:
                self.funcmap[extracted_op]()
            except:
                print("Unknown instruction: %X" % self.opcode)

    def _8ZZ2(self):
        log("Set Vx = Vx and Vy")
        self.gpio[self.vx]  = self.gpio[self.vx] & self.gpio[self.vy]

    def _8ZZ4(self):
        log("Adds Vy to Vx. Vf is set to 1 when there's a carry, and to 0 when there isn't")
        if(self.gpio[self.vx] + self.gpio[self.vy] > 0xff):
            self.gpio[0xf] = 1
        else:
            self.gpio[0xf] = 0
        self.gpio[self.vx] = (self.gpio[self.vx] + self.gpio[self.vy]) & 0xff

    def _8ZZ5(self):
        log("Subtracts Vy from Vx. Vf is set to 0 when there's a borrow, and to 1 otherwise")
        if(self.gpio[self.vx] > self.gpio[self.vy]):
            self.gpio[0xf] = 1
        else:
            self.gpio[0xf] = 0
        self.gpio[self.vx] = (self.gpio[self.vx] - self.gpio[self.vy]) & 0xff

    def _8ZZ6(self):
        log("Set Vx = Vx SHR 1")

        if self.gpio[self.vx] & 0x1 == 1:
            self.gpio[0xf] = 1
        else:
            self.gpio[0xf] = 0

        self.gpio[0xf] = self.gpio[0xf] << 1

    def _8ZZE(self):
        log("Set Vx = Vx SHL 1")

        if self.gpio[self.vx] >> 3 == 1:
            self.gpio[0xf] = 1
        else:
            self.gpio[0xf] = 0
            
        self.gpio[self.vx] = (self.gpio[self.vx] << 1) & 0xffff

    def _9ZZ0(self):
        log("Skip next instruction if Vx != Vy")

        if self.gpio[self.vx] != self.gpio[self.vy]:
            self.pc += 2

    def _AZZZ(self):
        log("Set I = nnn")
        self.index = self.opcode & 0x0fff

    def _CZZZ(self):
        log("Set Vx = random byte AND kk")
        random_byte = random.randint(0, 0xff)
        self.gpio[self.vx] = random_byte & (self.opcode & 0x00ff)

    def _DZZZ(self):
        log("Draw a sprite")
        self.gpio[0xf] = 0
        x = self.gpio[self.vx] & 0xff
        y = self.gpio[self.vy] & 0xff
        height = self.opcode & 0x000f
        row = 0
        while row < height:
            curr_row = self.memory[row + self.index]
            pixel_offset = 0
            while pixel_offset < 8:
                loc = x + pixel_offset + ((y + row)*64)
                pixel_offset += 1
                if (y + row) >= 32 or (x + pixel_offset - 1) >= 64:
                    #ignore pixels outside the screen
                    continue
                mask = 1 << 8 - pixel_offset
                curr_pixel = (curr_row & mask) >> (8-pixel_offset)
                self.display_buffer[loc] ^= curr_pixel
                if self.display_buffer[loc] == 0:
                    self.gpio[0xf] = 1
                else:
                    self.gpio[0xf] = 0
            row += 1
        self.should_draw = True

    def _EZZZ(self):
        extracted_op = self.opcode & 0xf0ff
        try:
            self.funcmap[extracted_op]()
        except:
            print("Unknown instruction: %X" % self.opcode)

    def _EZZE(self):
        log("Skips the next instruction if the key stores in Vx is pressed.")
        if self.key_inputs[self.gpio[self.vx] & 0xf ] == 1:
            self.pc += 2

    def _EZZ1(self):
        log("Skips the next instruction if the key with the value of Vx is not pressed")
        key = self.gpio[self.vx] & 0xf
        if self.key_inputs[key] == 0:
            self.pc += 2

    def _FZZZ(self):
        extracted_op = self.opcode & 0xf0ff
        try:
            self.funcmap[extracted_op]()
        except:
            print("Unknown instruction: %X" % self.opcode)

    def _FZ07(self):
        log("Set Vx = delay timer value")
        self.gpio[self.vx] = self.delay_timer

    def _FZ0A(self):
        log("Wait for a key press, store the value of the key in Vx")
        if self.key_wait == False:
            self.key_wait = True
            
        else:
            self.key_wait = False
            for key, val in self.key_inputs.items():
                if val == 1:
                    self.gpio[self.vx] = 1
                    return

    def _FZ15(self):
        log("Set delay timer = Vx")
        self.delay_timer = self.vx

    def _FZ18(self):
        log("Set sound timer = Vx")
        self.sound_timer = self.vx
    
    def _FZ1E(self):
        log("Set I = I + Vx")
        self.index = self.index + self.gpio[self.vx]

    def _FZ29(self):
        log("Set index to point to a character")
        self.index = (5*(self.gpio[self.vx])) & 0xfff

    def _FZ33(self):
        log("Store the BCD representation of Vx in memory locations I, I+1, and I+2")
        bcd = self.gpio[self.vx]

        self.memory[self.index] = bcd // 100
        self.memory[self.index + 1] = (bcd // 10) % 10
        self.memory[self.index + 2] = bcd % 10

    def _FZ55(self):
        log("Store registers V0 through Vx in memory starting at location I")
        
        register_counter = 0
        while register_counter <= self.vx:
            self.memory[self.index + register_counter] = self.gpio[register_counter]
            register_counter += 1

    def _FZ65(self):
        log("Read registers V0 through Vx in memory starting at location I")

        register_counter  = 0
        while register_counter <= self.vx:
            self.gpio[register_counter] = self.memory[self.index + register_counter]
            register_counter += 1


    def draw(self):
        if self.should_draw:
            self.clear()
            line_counter = 0
            i = 0
            while i < 2048:
                if self.display_buffer[i] == 1:
                    # draw a square pixel
                    self.pixel.update(x=(i % 64) * 10, y=310 - ((i // 64) * 10))
                    self.pixel.draw()
                i += 1
            self.flip()
            self.should_draw = False
    
    def on_key_press(self, symbol, modifiers):
        log("Key pressed: %r" % symbol)
        if symbol in KEY_MAP.keys():
            self.key_inputs[KEY_MAP[symbol]] = 1
        else:
            super(cpu, self).on_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        log("Key released: %r " % symbol)
        if symbol in KEY_MAP.keys():
            self.key_inputs[KEY_MAP[symbol]] = 0
    
def log(text_to_log):
    pass

KEY_MAP = {
    pyglet.window.key._1: 0x1,
    pyglet.window.key._2: 0x2,
    pyglet.window.key._3: 0x3,
    pyglet.window.key._4: 0xC,
    pyglet.window.key.Q: 0x4,
    pyglet.window.key.W: 0x5,
    pyglet.window.key.E: 0x6,
    pyglet.window.key.R: 0xD,
    pyglet.window.key.A: 0x7,
    pyglet.window.key.S: 0x8,
    pyglet.window.key.D: 0x9,
    pyglet.window.key.F: 0xE,
    pyglet.window.key.Z: 0xA,
    pyglet.window.key.X: 0x0,
    pyglet.window.key.C: 0xB,
    pyglet.window.key.V: 0xF
}

# begin emulating!
if len(sys.argv) == 3:
  if sys.argv[2] == "log":
    LOGGING = True
      
chip8emu = cpu(640, 320)
chip8emu.main()
log("... done.")