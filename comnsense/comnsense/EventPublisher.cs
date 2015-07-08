using System;
using System.Text;
using Newtonsoft.Json;
using ZeroMQ;

namespace comnsense
{
    /// <summary>
    ///  EventPublisher binds to a ZMQ Context and can publish Events to it to Router
    /// </summary>
    internal class EventPublisher : IDisposable
    {
        public const string RouterAddress = "inproc://events";
        private readonly ZSocket _socket;

        public EventPublisher(ZContext context)
        {
            _socket = new ZSocket(context, ZSocketType.PUB);
            _socket.Bind(RouterAddress);
        }

        public void Send(Event @event)
        {
            var data = JsonConvert.SerializeObject(
                @event, 
                Formatting.None, 
                new JsonSerializerSettings {NullValueHandling = NullValueHandling.Ignore});

            using (var message = new ZMessage())
            {
                message.Add(new ZFrame(Encoding.UTF8.GetBytes(@event.workbook)));
                message.Add(new ZFrame(Encoding.UTF8.GetBytes(data)));
                _socket.Send(message);
            }
        }

        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }

        ~EventPublisher()
        {
            Dispose(false);
        }

        protected virtual void Dispose(bool disposing)
        {
            if (disposing)
                if (_socket != null)
                    _socket.Dispose();
        }
    }
}
