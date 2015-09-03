using System;
using System.Linq;
using Microsoft.Office.Core;

namespace Comnsense.ExcelAddin
{
    public static class DocumentPropertiesExtensions
    {
        public static string GetStringPropertyValue(
            this DocumentProperties properties,
            string propertyName)
        {
            if (properties == null)
                throw new ArgumentNullException(nameof(properties));
            if (propertyName == null)
                throw new ArgumentNullException(nameof(propertyName));

            return (string) properties.FindStringPropertyByName(propertyName)?.Value ?? "";
        }

        private static DocumentProperty FindStringPropertyByName(
            this DocumentProperties properties,
            string propertyName)
        {
            return properties.Cast<DocumentProperty>()
                .FirstOrDefault(
                    p => p.Name == propertyName &&
                         p.Type == MsoDocProperties.msoPropertyTypeString);
        }

        public static void SetStringPropertyValue(
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

            var result = properties.FindStringPropertyByName(propertyName);

            if (result == null)
                properties.Add(propertyName, false, MsoDocProperties.msoPropertyTypeString, value, null);
            else
                result.Value = value;
        }
    }
}