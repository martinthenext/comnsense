using System;
using System.IO;
using System.Runtime.Serialization;
using Newtonsoft.Json;

namespace Comnsense.ExcelAddin.Data
{
    public class JsonNetSerializer : ISerializer
    {
        public static JsonSerializerSettings DefaultSettings => 
            new JsonSerializerSettings
            {
                NullValueHandling = NullValueHandling.Ignore,
                Formatting = Formatting.None
            };

        public JsonNetSerializer() : this(DefaultSettings) { }

        public JsonNetSerializer(JsonSerializerSettings settings)
        {
            if (settings == null)
                throw new ArgumentNullException(nameof(settings));

            Settings = settings;
        }

        public JsonSerializerSettings Settings { get; }

        public void Serialize(object value, Stream output)
        {
            if (value == null)
                throw new ArgumentNullException(nameof(value));
            if (output == null)
                throw new ArgumentNullException(nameof(output));

            try
            {
                var serializer = JsonSerializer.Create(Settings);

                using (var streamWriter = new StreamWriter(output))
                using (var jsonWriter = new JsonTextWriter(streamWriter))
                    serializer.Serialize(jsonWriter, value);
            }
            catch (JsonException exception)
            {
                throw new SerializationException(
                    "Exception occurred while serializing",
                    exception);
            }
        }

        public T Deserialize<T>(Stream input)
        {
            if (input == null)
                throw new ArgumentNullException(nameof(input));

            try
            {
                var serializer = JsonSerializer.Create(Settings);

                using (var streamReader = new StreamReader(input))
                using (var jsonReader = new JsonTextReader(streamReader))
                    return serializer.Deserialize<T>(jsonReader);
            }
            catch (JsonException exception)
            {
                throw new SerializationException(
                    "Exception occurred while deserializing",
                    exception);
            }
        }
    }
}