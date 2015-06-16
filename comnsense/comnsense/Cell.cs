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
        public string key; // Cell address
        public string value; // Cell value
        public bool[] borders;
        public string font; // Font name
        public int color; // Excel color index
        public int fontstyle; // Format bit mask:
    }
}
