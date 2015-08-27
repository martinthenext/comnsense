using System.IO;

namespace comnsense.Data
{
    public interface ISerializer
    {
        void Serialize(object value, Stream output);
        T Deserialize<T>(Stream input);
    }
}