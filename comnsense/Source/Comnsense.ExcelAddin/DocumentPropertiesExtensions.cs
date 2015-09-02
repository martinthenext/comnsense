using System;
using System.Linq;
using Microsoft.Office.Core;

namespace Comnsense.ExcelAddin
{
    public static class DocumentPropertiesExtensions
    {
        public static string GetStringProperty(
            this DocumentProperties properties,
            string propertyName)
        {
            if (properties == null)
                throw new ArgumentNullException(nameof(properties));
            if (propertyName == null)
                throw new ArgumentNullException(nameof(propertyName));

            var result = properties.Cast<DocumentProperty>()
                .FirstOrDefault(
                    p => p.Name == propertyName && 
                    p.Type == MsoDocProperties.msoPropertyTypeString);
            return (string) result?.Value ?? "";
        }

        public static void SetStringProperty(
            this DocumentProperties properties, 
            string propertyName, 
            string value)
        {
            if (properties == null)
                throw new ArgumentNullException(nameof(properties));
            if (propertyName == null)
                throw new ArgumentNullException(nameof(propertyName));
            if (value == null)
                throw new ArgumentNullException(nameof(value));

            if (properties.GetStringProperty(propertyName) != "")
                properties[propertyName].Delete();
            properties.Add(propertyName, false, MsoDocProperties.msoPropertyTypeString, value);
        }
    }
}