import unittest
from motion import PWDCmd
class TestMotion(unittest.TestCase):
    def test_twos_comp(self):
        p = PWDCmd()
        hex_string = ["03", "00", "77", "12", "34" ]
        #x = p.twos_comp(int(hex_string, 16),8)
        #bytes_str = ''.join('{:02x}'.format(x))
        #print bytes_str
        hex_bytes = [int(x, 16) for x in hex_string]
        print hex_bytes
        print ''.join('{:02x}'.format(sum(hex_bytes)))
        x = p.twos_comp(sum(hex_bytes),8)
        x &= ~0xf
        print '{:02x}'.format(x )
        #print '{:02x}'.format(~0xC0 )

    def test_checksum_framemethod(self):
        p = PWDCmd()
        frames= [[0x01, 0x00, 0x00, 0x39],
            [0x03, 0x00, 0x77, 0x12, 0x34],
            [0x01, 0x00, 0x7F, 0x00, 0x80],
            [0x01, 0x00, 0xa0],
            [0x01, 0x00, 0x90]],
        [self.checksum_check(f) for f in frames[0]]

    def checksum_check(self, frame):
        p = PWDCmd()
        checksum = p.twos_comp(sum(frame), 8 )
        #print "check_sum",  '{:02x}'.format(checksum)
        frame[1] = checksum
        print ['{:02x}'.format(x) for x in frame]
        frame_sum = sum(frame) & 0xFF
        print "frame_sum",  '{:02x}'.format(frame_sum)
        self.assertTrue(frame_sum == 0x00)
        
if __name__ == "__main__":
    unittest.main()