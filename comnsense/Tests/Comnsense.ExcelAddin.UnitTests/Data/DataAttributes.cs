using System.Globalization;
using Ploeh.AutoFixture;
using Ploeh.AutoFixture.AutoNSubstitute;
using Ploeh.AutoFixture.Xunit2;

namespace Comnsense.ExcelAddin.UnitTests.Data
{
    public class SerializerAutoDataAttribute : AutoDataAttribute
    {
        public SerializerAutoDataAttribute()
            : base(new Fixture().Customize(new AutoNSubstituteCustomization()))
        {
            Fixture.Inject(CultureInfo.InvariantCulture);
        }
    }
}