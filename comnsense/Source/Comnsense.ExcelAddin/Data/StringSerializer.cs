using System;
using System.IO;
using System.Text;

namespace Comnsense.ExcelAddin.Data
{
    public static class StringSerializer
    {
        public static string SerializeAsString(
            this ISerializer serializer,
            object value) => SerializeAsString(serializer, value, Encoding.UTF8);

        public static string SerializeAsString(
            this ISerializer serializer,
            object value,
            Encoding encoding)
        {
            if (serializer == null)
                throw new ArgumentNullException(nameof(serializer));
            if (value == null)
                throw new ArgumentNullException(nameof(value));
            if (encoding == null)
                throw new ArgumentNullException(nameof(encoding));

            using (var stream = new MemoryStream())
            {
                serializer.Serialize(value, stream);
                return encoding.GetString(stream.ToArray());
            }
        }

        public static T DeserializeFromString<T>(
            this ISerializer serializer,
            string value) => DeserializeFromString<T>(serializer, value, Encoding.UTF8);

        public static T DeserializeFromString<T>(
            this ISerializer serializer,
            string value,
            Encoding encoding)
        {
            if (serializer == null)
                throw new ArgumentNullException(nameof(serializer));
            if (value == null)
                throw new ArgumentNullException(nameof(value));
            if (encoding == null)
                throw new ArgumentNullException(nameof(encoding));

            using (Stream stream = new MemoryStream(encoding.GetBytes(value)))
                return serializer.Deserialize<T>(stream);
        }
    }
}