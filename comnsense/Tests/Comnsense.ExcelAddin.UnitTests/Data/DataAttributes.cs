using System.Globalization;
using System.Text;
using Ploeh.AutoFixture;

namespace Comnsense.ExcelAddin.UnitTests.Data
{
    public class SerializerAutoDataAttribute : AutoMockDataAttribute
    {
        public SerializerAutoDataAttribute()
        {
            Fixture.Inject(CultureInfo.InvariantCulture);
            Fixture.Inject(Encoding.UTF8);
        }
    }
}