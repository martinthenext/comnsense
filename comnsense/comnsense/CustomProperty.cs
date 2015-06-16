/*
 * This file handles the ComnsenseID - a unique identifier of an Excel file 
 * 
*/
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
            this.cached = null;
        }


        public String get(String def = null) {
            if (cached != null)
            {
                return cached;
            }
            dynamic properties = this.wb.CustomDocumentProperties;
            foreach (dynamic prop in properties)
            {
                if (prop.Name == this.key)
                {

                    cached = prop.Value.ToString();
                    return cached;
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
            cached = ident;
        }

        private String key;
        private Excel.Workbook wb;
        private String cached;
    }
}
