using System.IO;
using System.Text;
using Comnsense.ExcelAddin.Data;
using Ploeh.AutoFixture.Idioms;
using Ploeh.AutoFixture.Xunit2;
using Xunit;

namespace Comnsense.ExcelAddin.UnitTests.Data
{
    public class StringSerializerTestCase
    {
        [Theory, SerializerAutoData]
        public void AllMembers_Always_ShouldHaveNullGuards(GuardClauseAssertion assertion) 
            => assertion.Verify(typeof (StringSerializer));

        [Theory, SerializerAutoData]
        public void SerializeAsString_WithValidArguments_ShouldReturnExpectedResult(
            [Frozen] string expected,
            SerializerSpy sut,
            object input,
            Encoding encoding)
        {
            var actual = sut.SerializeAsString(input, encoding);
            Assert.Equal(expected, actual);
        }

        [Theory, SerializerAutoData]
        public void DeserializeAsString_WithValidArguments_ShouldCallDeserialize<T>(
            SerializerSpy sut,
            string input,
            Encoding encoding)
        {
            sut.DeserializeFromString<T>(input, encoding);
            Assert.Equal(input, sut.DeserializationContent);
        }

        public class SerializerSpy : ISerializer
        {
            private readonly Encoding _encoding;

            public SerializerSpy(Encoding encoding)
            {
                _encoding = encoding;
            }

            public string SerializationContent { get; set; }
            public string DeserializationContent { get; private set; }

            public void Serialize(object value, Stream output)
            {
                var content = _encoding.GetBytes(SerializationContent);
                output.Write(content, 0, content.Length);
            }

            public T Deserialize<T>(Stream input)
            {
                using (var reader = new StreamReader(input, _encoding))
                    DeserializationContent = reader.ReadToEnd();
                return default(T);
            }
        }
    }
}