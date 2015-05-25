using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using ZeroMQ;

namespace comnsense
{
    class EventPublisher: IDisposable
    {
        public static const string Address = "inproc://events";

        public EventPublisher(ZContext ctx)
        {
            this.socket = new ZSocket(ctx, ZSocketType.PUB);
            this.socket.Bind(EventPublisher.Address);
        }

        public void Send(Event evt) {

        }

        public ~EventPublisher()
        {
            this.Dispose();

        }

        public void Dispose()
        {
            this.socket.Dispose();
        }

        private ZSocket socket;
    }
}
