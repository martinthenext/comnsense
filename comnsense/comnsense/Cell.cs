using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace comnsense
{
    [Serializable()]
    class Cell
    {
        public string key;
        public string value;
        public bool[] borders;
        public string font;
        public int color;
        public int fontstyle;
    }
}
