using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Excel = Microsoft.Office.Interop.Excel;


namespace comnsense
{
    [Serializable()]
    class Borders
    {
        // Tuples (weight, line style) 
        // (Excel.XlBorderWeight, Excel.XlLineStyle) encoded in ints
        public int[] top;
        public int[] bottom;
        public int[] left;
        public int[] right;
    }


    [Serializable()]
    class Cell
    {
        public string key; // Cell address
        public string value; // Cell value
        public string font; // Font name
        public byte color; // Excel ColorIndex
        public byte fontstyle; // Format bit mask: bold, italic, underline
        public Borders borders;
    }
}
