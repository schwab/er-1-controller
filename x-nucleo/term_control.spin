CON
  _clkmode = xtal1 + pll16x
  _xinfreq = 5_000_000
  clk_freq = (_clkmode >> 6) * _xinfreq 
OBJ   
  pst  : "Parallax Serial Terminal"
  time : "Timing"   
PUB  Main | value      
  pst.Start(115_200)
  WAITCNT((1*(clkfreq)) + cnt)
  pst.Str(String("Testing of PowerStep1 driver over SPI bus. ENTER to begin."))
  repeat
     'pst.Str(String(" Test "))
'     pst.NewLine
     'pst.LineFeed
     'pst.Position (1,19)
     pst.Hex ($0D, 2)
     time.pause1ms(1000)            