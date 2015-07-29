using System;
using Microsoft.Office.Interop.Excel;
using Microsoft.Office.Core;

namespace comnsense
{
    /// <summary>
    /// This class handles the ComnsenseID - a unique identifier of an Excel file
    /// </summary>
    internal class CustomProperty
    {
        private string key;
        private Workbook wb;
        private string cached;

        public CustomProperty(string key, Workbook wb)
        {
            this.key = key;
            this.wb = wb;
        }

        public string Get(string def = null)
        {
            if (cached != null)
                return cached;

            var properties = (DocumentProperties)wb.CustomDocumentProperties;
            foreach (DocumentProperty prop in properties)
            {
                if (prop.Name != key)
                    continue;
                cached = prop.Value.ToString();
                return cached;
            }
            return def;
        }

        public void Set(string ident)
        {
            var properties = (DocumentProperties) wb.CustomDocumentProperties;
            if (Get() != null)
                properties[key].Delete();
            properties.Add(key, false, MsoDocProperties.msoPropertyTypeString, ident);
            cached = ident;
        }
    }
}
