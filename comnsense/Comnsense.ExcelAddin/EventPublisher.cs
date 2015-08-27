using System;
using System.Text;
using Comnsense.ExcelAddin.Data;
using ZeroMQ;

namespace Comnsense.ExcelAddin
{
    /// <summary>
    ///  EventPublisher binds to a ZMQ Context and can publish Events to it to Router
    /// </summary>
    internal class EventPublisher : IDisposable
    {
        public const string RouterAddress = "inproc://events";
        private readonly ZSocket _socket;
        private readonly ISerializer _serializer;

        public EventPublisher(ZContext context, ISerializer serializer)
        {
            if (context == null)
                throw new ArgumentNullException(nameof(context));
            if (serializer == null)
                throw new ArgumentNullException(nameof(serializer));

            _socket = new ZSocket(context, ZSocketType.PUB);
            _socket.Bind(RouterAddress);
            _serializer = serializer;
        }

        public void Send(Event @event)
        {
            var data = _serializer.SerializeAsString(@event);
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
                _socket?.Dispose();
        }
    }
}
