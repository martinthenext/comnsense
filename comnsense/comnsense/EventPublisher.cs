/*
 * EventPublisher binds to a ZMQ Context and can publish Events to it to Router
 */

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using ZeroMQ;
using Json = Newtonsoft.Json;

namespace comnsense
{
    class EventPublisher: IDisposable
    {
        public const string RouterAddress = "inproc://events";

        public EventPublisher(ZContext ctx)
        {
            this.socket = new ZSocket(ctx, ZSocketType.PUB);
            this.socket.Bind(EventPublisher.RouterAddress);
        }

        public void Send(Event evt) {
            String data = Json.JsonConvert.SerializeObject(
                evt, Json.Formatting.None, 
                new Json.JsonSerializerSettings 
                    {
                        NullValueHandling = Json.NullValueHandling.Ignore 
                    });
            using (var message = new ZMessage())
            {
                message.Add(new ZFrame(Encoding.UTF8.GetBytes(evt.workbook)));
                message.Add(new ZFrame(Encoding.UTF8.GetBytes(data)));
                this.socket.Send(message);
            }
        }

        ~EventPublisher()
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
