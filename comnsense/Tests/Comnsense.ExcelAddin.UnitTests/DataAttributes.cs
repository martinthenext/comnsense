using Ploeh.AutoFixture;
using Ploeh.AutoFixture.AutoNSubstitute;
using Ploeh.AutoFixture.Xunit2;

namespace Comnsense.ExcelAddin.UnitTests
{
    public class AutoMockDataAttribute : AutoDataAttribute
    {
        public AutoMockDataAttribute()
            : base(new Fixture().Customize(
                new AutoNSubstituteCustomization()))
        {
        }
    }
}