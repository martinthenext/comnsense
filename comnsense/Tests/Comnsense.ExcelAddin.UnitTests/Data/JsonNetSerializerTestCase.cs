using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.Serialization;
using Comnsense.ExcelAddin.Data;
using Newtonsoft.Json;
using Ploeh.AutoFixture;
using Ploeh.AutoFixture.Idioms;
using Ploeh.AutoFixture.Xunit2;
using Ploeh.SemanticComparison;
using Xunit;

namespace Comnsense.ExcelAddin.UnitTests.Data
{
    public class JsonNetSerializerTestCase
    {
        private static JsonNetSerializer CreateSystemUnderTest()
        {
            return new JsonNetSerializer(JsonNetSerializer.DefaultSettings);
        }

        [Theory, AutoData]
        public void SutIsISerializer(JsonNetSerializer sut)
        {
            Assert.IsAssignableFrom<ISerializer>(sut);
        }

        [Theory, SerializerAutoData]
        public void AllMembers_Always_ShouldHaveNullGuards(
            [Frozen] Fixture fixture,
            GuardClauseAssertion assertion)
        {
            using (Stream stream = new MemoryStream())
            {
                fixture.Inject(stream);
                assertion.Verify(typeof(JsonNetSerializer));
            }
        }

        [Theory, MemberData("SerializationTestData")]
        public void Serialize_WithDefaultSettings_ShouldReturnExpectedResult(
            object input,
            string expected)
        {
            var sut = CreateSystemUnderTest();
            var actual = sut.SerializeAsString(input);
            Assert.Equal(expected, actual);
        }

        public static IEnumerable<object[]> SerializationTestData
        {
            get
            {
                // Should serialize "empty" values 
                // (e.g. empty strings, 0 for integers, false for booleans, etc.)
                yield return new object[]
                {
                    new Victim {FirstName = ""},
                    "{\"firstName\":\"\",\"age\":0,\"isGoodEnough\":false}"
                };

                // Should ignore null values
                yield return new object[]
                {
                    new Victim(),
                    "{\"age\":0,\"isGoodEnough\":false}"
                };

                // Should serialize values with camelCase
                yield return new object[]
                {
                    new Victim {FirstName = "Vasya", Age = 25, IsGoodEnough = true},
                    "{\"firstName\":\"Vasya\",\"age\":25,\"isGoodEnough\":true}"
                };

                // Should keep casing when serializing dictionaries
                yield return new object[]
                {
                    new Dictionary<string, string>
                    {
                        {"FirstKey", "foo"},
                        {"secondKey", "bar"}
                    },
                    "{\"FirstKey\":\"foo\",\"secondKey\":\"bar\"}"
                };
            }
        }

        [Theory, AutoData]
        public void Serialize_WithInvalidInput_ShouldThrowSerializationException(
            JsonNetSerializer sut,
            NotImplementedClass invalidInput)
        {
            var actual = Assert.Throws<SerializationException>(
                () => sut.SerializeAsString(invalidInput));
            Assert.IsAssignableFrom<JsonException>(actual.InnerException);
        }

        [Theory, MemberData("DeserializationTestData")]
        public void Deserialize_WithDefaultSettings_ShouldReturnExpectedResult<T>(
            string input,
            T expected)
        {
            var sut = CreateSystemUnderTest();
            var actual = sut.DeserializeFromString<T>(input);
            Assert.Equal(expected, actual, new SemanticComparer<T>());
        }

        public static IEnumerable<object[]> DeserializationTestData
        {
            get
            {
                // Should ignore missing properties while deserialization
                yield return new object[]
                {
                    "{\"firstName\":\"Vasya\",\"age\":25,\"missingProperty\":\"foo\"}",
                    new Victim {FirstName = "Vasya", Age = 25}
                };
            }
        }

        [Theory, AutoData]
        public void Deserialize_WithInvalidInput_ShouldThrowSerializationException<T>(
            JsonNetSerializer sut,
            string invalidInput)
        {
            var actual = Assert.Throws<SerializationException>(
                () => sut.DeserializeFromString<T>(invalidInput));
            Assert.IsAssignableFrom<JsonException>(actual.InnerException);
        }

        public class Victim
        {
            public string FirstName { get; set; }
            public int Age { get; set; }
            public bool IsGoodEnough { get; set; }
        }

        public class NotImplementedClass
        {
            public object NotImplementedProperty
            {
                get { throw new NotImplementedException(); }
            }
        }
    }
}