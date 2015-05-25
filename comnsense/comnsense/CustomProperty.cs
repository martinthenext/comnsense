using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Excel = Microsoft.Office.Interop.Excel;
using Office = Microsoft.Office.Core;

namespace comnsense
{
    class CustomProperty
    {
        public CustomProperty(String key, Excel.Workbook wb)
        {
            this.key = key;
            this.wb = wb;
        }


        public String get(String def = null) {
            Office.DocumentProperties properties = (Office.DocumentProperties)this.wb.CustomDocumentProperties;
            foreach (Office.DocumentProperty prop in properties)
            {
                if (prop.Name == this.key)
                {
                    return prop.Value.ToString();
                }
            }
            return def;
        }

        public void set(String ident)
        {
            Office.DocumentProperties properties = (Office.DocumentProperties)this.wb.CustomDocumentProperties;
            if (this.get() != null)
            {
                properties[this.key].Delete();
            }
            properties.Add(this.key, false, Office.MsoDocProperties.msoPropertyTypeString, ident);
        }

        private String key;
        private Excel.Workbook wb;
    }
}
