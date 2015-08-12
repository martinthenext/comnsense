using Microsoft.Office.Interop.Excel;
using Microsoft.Office.Core;

namespace comnsense
{
    /// <summary>
    /// This class handles the ComnsenseID - a unique identifier of an Excel file
    /// </summary>
    internal class CustomProperty
    {
        private readonly string _key;
        private readonly Workbook _workbook;
        private string _cache;

        public CustomProperty(string key, Workbook workbook)
        {
            _key = key;
            _workbook = workbook;
        }

        public string Get(string def = null)
        {
            if (_cache != null)
                return _cache;

            DocumentProperties properties = _workbook.CustomDocumentProperties;
            foreach (DocumentProperty prop in properties)
            {
                if (prop.Name != _key)
                    continue;
                _cache = prop.Value.ToString();
                return _cache;
            }
            return def;
        }

        public void Set(string ident)
        {
            DocumentProperties properties = _workbook.CustomDocumentProperties;
            if (Get() != null)
                properties[_key].Delete();
            properties.Add(_key, false, MsoDocProperties.msoPropertyTypeString, ident);
            _cache = ident;
        }
    }
}
