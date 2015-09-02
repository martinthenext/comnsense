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

        [Theory, MemberData("GetStringPropertyTestData")]
        public void GetStringProperty_WithValidArguments_ShouldReturnExpectedResult(
            IEnumerable<DocumentProperty> properties,
            string input,
            string expected)
        {
            var sut = Substitute.For<DocumentProperties>();
            ((IEnumerable) sut).GetEnumerator().Returns(properties.GetEnumerator());

            var actual = sut.GetStringProperty(input);

            Assert.Equal(expected, actual);
        }

        public static IEnumerable<object> GetStringPropertyTestData
        {
            get
            {
                var fixture = new Fixture().Customize(new AutoConfiguredNSubstituteCustomization());

                // Should return empty string if property wasn't found
                yield return new object[]
                {
                    fixture.CreateMany<DocumentProperty>(),
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
    }
}