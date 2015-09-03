using System.Collections;
using System.Collections.Generic;
using System.Linq;
using Microsoft.Office.Core;
using NSubstitute;
using Ploeh.AutoFixture;
using Ploeh.AutoFixture.AutoNSubstitute;
using Ploeh.AutoFixture.Idioms;
using Xunit;

namespace Comnsense.ExcelAddin.UnitTests
{
    public class DocumentPropertiesExtensionsTestCase
    {
        [Theory, AutoMockData]
        public void AllMembers_Always_ShouldHaveNullGuard(GuardClauseAssertion assertion)
            => assertion.Verify(typeof (DocumentPropertiesExtensions));

        [Theory, MemberData("GetStringPropertyValueTestData")]
        public void GetStringPropertyValue_WithValidArguments_ShouldReturnExpectedResult(
            IEnumerable<DocumentProperty> properties,
            string input,
            string expected)
        {
            var sut = new DocumentPropertiesFake(properties);
            var actual = sut.GetStringPropertyValue(input);
            Assert.Equal(expected, actual);
        }

        public static IEnumerable<object> GetStringPropertyValueTestData
        {
            get
            {
                var fixture = new Fixture().Customize(new AutoConfiguredNSubstituteCustomization());

                // Should return empty string if property wasn't found
                yield return new object[]
                {
                    fixture.CreateMany<DocumentProperty>().ToArray(),
                    fixture.Create<string>(),
                    ""
                };

                // Should return property value if proper property found
                // Proper property should be of MsoDocProperties.msoPropertyTypeString type
                // and have appropriate name
                yield return new object[]
                {
                    fixture.CreateMany<DocumentProperty>().Concat(new []
                    {
                        fixture.Build<DocumentProperty>()
                            .FromFactory(() => Substitute.For<DocumentProperty>())
                            .With(x => x.Name, "foo")
                            .With(x => x.Value, "bar")
                            .With(x => x.Type, MsoDocProperties.msoPropertyTypeString)
                            .Create()
                    }),
                    "foo",
                    "bar"
                };

                // Should return empty string if proper property found
                // but it have null value
                yield return new object[]
                {
                    fixture.CreateMany<DocumentProperty>().Concat(new []
                    {
                        fixture.Build<DocumentProperty>()
                            .FromFactory(() => Substitute.For<DocumentProperty>())
                            .With(x => x.Name, "foo")
                            .With(x => x.Value, null)
                            .With(x => x.Type, MsoDocProperties.msoPropertyTypeString)
                            .Create()
                    }),
                    "foo",
                    ""
                };

                // Should return empty string for empty DocumentProperties
                yield return new object[]
                {
                    new DocumentProperty[] {},
                    fixture.Create<string>(),
                    ""
                };

                // Should return empty string if property with appropriate name exists
                // but have other than MsoDocProperties.msoPropertyTypeString type
                yield return new object[]
                {
                    fixture.CreateMany<DocumentProperty>().Concat(new[]
                    {
                        fixture.Build<DocumentProperty>()
                            .FromFactory(() => Substitute.For<DocumentProperty>())
                            .With(x => x.Name, "foo")
                            .With(x => x.Value, "bar")
                            .With(
                                x => x.Type, 
                                fixture.Create<Generator<MsoDocProperties>>()
                                    .First(x => x != MsoDocProperties.msoPropertyTypeString))
                            .Create()
                    }),
                    "foo",
                    ""
                };
            }
        }

        [Theory, MemberData("SetStringPropertyValueTestData")]
        public void SetStringProperty_WithValidArguments_ShouldReturnExpectedResult(
            IEnumerable<DocumentProperty> properties,
            string propertyName,
            string expected)
        {
            var sut = new DocumentPropertiesFake(properties);
            sut.SetStringPropertyValue(propertyName, expected);
            Assert.Single(sut.Seed, p => p.Name == propertyName && p.Value == expected);
        }

        public static IEnumerable<object[]> SetStringPropertyValueTestData
        {
            get
            {
                var fixture = new Fixture().Customize(new AutoConfiguredNSubstituteCustomization());

                // Should add new string property if properties doesn't contain
                // property with appropriate name
                yield return new object[]
                {
                    fixture.CreateMany<DocumentProperty>().ToArray(),
                    "foo",
                    "bar"
                };

                // Should replace value of existing property
                yield return new object[]
                {
                    fixture.CreateMany<DocumentProperty>().Concat(new []
                    {
                        fixture.Build<DocumentProperty>()
                            .FromFactory(() => Substitute.For<DocumentProperty>())
                            .With(x => x.Name, "foo")
                            .With(x => x.Value, "bar")
                            .With(x => x.Type, MsoDocProperties.msoPropertyTypeString)
                            .Create()
                    }),
                    "foo",
                    "baz"
                };
            }
        }

        private class DocumentPropertiesFake : DocumentProperties
        {
            public DocumentPropertiesFake(IEnumerable<DocumentProperty> seed)
            {
                Seed = seed.ToList();
            }

            public IList<DocumentProperty> Seed { get; }

            public DocumentProperty Add(
                string name, 
                bool linkToContent, 
                object type,
                object value, 
                object linkSource)
            {
                var newProperty = new Fixture().Build<DocumentProperty>()
                    .FromFactory(() => Substitute.For<DocumentProperty>())
                    .With(x => x.Name, name)
                    .With(x => x.LinkToContent, linkToContent)
                    .With(x => x.Type, (MsoDocProperties) type)
                    .With(x => x.Value, value)
                    .With(x => x.LinkSource, linkSource)
                    .Create();
                Seed.Add(newProperty);
                return newProperty;
            }

            IEnumerator DocumentProperties.GetEnumerator() => Seed.GetEnumerator();
            IEnumerator IEnumerable.GetEnumerator() => Seed.GetEnumerator();
            public DocumentProperty this[object index] => null;
            public int Count => Seed.Count;

            public object Application { get; }
            public object Parent { get; }
            public int Creator { get; }
        }
    }
}