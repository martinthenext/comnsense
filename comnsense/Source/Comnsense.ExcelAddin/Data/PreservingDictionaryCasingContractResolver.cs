using System;
using Newtonsoft.Json.Serialization;

namespace Comnsense.ExcelAddin.Data
{
    public class PreservingDictionaryCasingContractResolver
        : CamelCasePropertyNamesContractResolver
    {
        protected override JsonDictionaryContract CreateDictionaryContract(
            Type objectType)
        {
            var contract = base.CreateDictionaryContract(objectType);
            contract.DictionaryKeyResolver = name => name;
            return contract;
        }
    }
}