using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace comnsense
{
    class EventSerializer : IDisposable
    {
        public static const string Version = "1"; 

        public EventSerializer()
        {

        }

        public void Dispose()
        {
            if (!this.disposed)
            {
                // do somethig
                disposed = true;
            }
        }

        public ~EventSerializer()
        {
            Dispose();
        }

        private bool disposed = false;
    }
}
