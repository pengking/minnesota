# Copyright (c) 2011-2013 Christopher Felton
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
The following is the HDL description of the stroby LED.
This module requires MyHDL >= 0.8.

Full tutorial available at :
http://www.fpgarelated.com/showarticle/25.php
"""

from myhdl import *

def m_led_stroby(
  # ~~~[Ports]~~~
  clock,             # input : system sync clock
  reset,             # input : reset (level determined by RST_LEVEL)
  leds,              # output : to IO ports drive LEDs

  # ~~~[Parameters]~~~
  led_rate = 333e-3, # strobe change rate of 333ms
  num_dumb = 4,      # The number of dummy LEDS on each side
):
    """ strobe the LED
    """

    # Number of LEDs
    led_bank = len(leds)
    
    # Need to calculate some constants.  Want the value to
    # be an integer (non-fractional value only whole number)
    cnt_max = int(clock.frequency * led_rate)   
    
    # Some useful definitions (constants)
    mb = led_bank + 2*num_dumb
    lsb,msb = (0,mb-1,)
    msb_reverse_val = (1 << mb-2)
    lsb_reverse_val = 2
    
    # Declare the internal Signals in our design
    led_bit_mem    = Signal(intbv(1)[mb:])
    left_not_right = Signal(True)
    clk_cnt        = Signal(intbv(0, min=0, max=cnt_max))
    strobe         = Signal(False)

    @always_seq(clock.posedge, reset=reset)
    def rtl_beh():
        # Generate the strobe event, use the "greater
        # than" for initial condition cases.  Count the
        # number of clock ticks that equals the LED strobe rate
        if clk_cnt >= cnt_max-1:
            clk_cnt.next = 0
            strobe.next  = True
        else:
            clk_cnt.next = clk_cnt + 1
            strobe.next  = False
        
        # The following always changes direction and "resets" when
        # either the lsb or msb is set.  This handles our initial 
        # condition as well.
        if strobe:
            if led_bit_mem[msb]:
                led_bit_mem.next = msb_reverse_val
                left_not_right.next = False
            elif led_bit_mem[lsb]:
                led_bit_mem.next = lsb_reverse_val
                left_not_right.next = True
            else:
                if left_not_right:
                    led_bit_mem.next = led_bit_mem << 1
                else:
                    led_bit_mem.next = led_bit_mem >> 1

    @always_comb
    def rtl_map_output():
        leds.next = led_bit_mem[led_bank+num_dumb:num_dumb]
        
    return rtl_beh, rtl_map_output

