using System.Globalization;
using Ploeh.AutoFixture;

namespace Comnsense.ExcelAddin.UnitTests.Data
{
    public class SerializerAutoDataAttribute : AutoMockDataAttribute
    {
        public SerializerAutoDataAttribute()
        {
            Fixture.Inject(CultureInfo.InvariantCulture);
        }
    }
}