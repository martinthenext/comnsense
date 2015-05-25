using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Excel = Microsoft.Office.Interop.Excel;

namespace comnsense
{
    class Ident : CustomProperty
    {
        public Ident(Excel.Workbook wb) : base("ComnsenseID", wb)
        {
            
        }

        public String ToString() {
            return this.get();
        }
    }
}
