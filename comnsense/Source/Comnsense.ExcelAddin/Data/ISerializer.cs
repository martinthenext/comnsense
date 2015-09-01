using System.IO;

namespace Comnsense.ExcelAddin.Data
{
    public interface ISerializer
    {
        void Serialize(object value, Stream output);
        T Deserialize<T>(Stream input);
    }
}