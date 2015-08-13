using System;
using Microsoft.Office.Interop.Excel;

namespace comnsense
{
    internal class Ident : CustomProperty
    {
        public Ident(Workbook workbook) : base("ComnsenseID", workbook) { }

        public override string ToString()
        {
            return Get();
        }
    }
}
