using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace comnsense
{
    [Serializable()]
    class Action
    {
        public enum ActionType
        {
            ComnsenseChange = 0,
            RangeRequest = 1
        }

        public ActionType type;
        public string workbook;
        public string sheet;

        // ComnsenseChange - related
        public string changeid;
        public Cell[][] cells;
        public bool font;
        public bool borders;
        public bool color;
        public bool fontstyle;

        // RangeRequest - related
        public string rangeName; 
    }
}
