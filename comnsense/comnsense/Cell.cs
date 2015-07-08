using System;

namespace comnsense
{
    [Serializable]
    internal class Borders
    {
        // Tuples (weight, line style) 
        // (Excel.XlBorderWeight, Excel.XlLineStyle) encoded in ints
        public int[] top;
        public int[] bottom;
        public int[] left;
        public int[] right;
    }

    /* Possible int values for the tuples
     
    XlBorderWeight
        xlMedium = -4138,
        xlHairline = 1,
        xlThin = 2,
        xlThick = 4,

    XlLineStyle
        xlLineStyleNone = -4142,
        xlDouble = -4119,
        xlDot = -4118,
        xlDash = -4115,
        xlContinuous = 1,
        xlDashDot = 4,
        xlDashDotDot = 5,
        xlSlantDashDot = 13,
    
    */

    [Serializable]
    internal class Cell
    {
        public string key; // Cell address
        public string value; // Cell value
        public string font; // Font name
        public byte? color = null; // Excel ColorIndex
        public byte? fontstyle = null; // Format bit mask: bold, italic, underline
        public Borders borders;
    }
}
