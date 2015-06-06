﻿using System;
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
        public const string Address = "inproc://events";

        public EventPublisher(ZContext ctx)
        {
            this.socket = new ZSocket(ctx, ZSocketType.PUB);
            this.socket.Bind(EventPublisher.Address);
        }

        public void Send(Event evt) {
            String data = Json.JsonConvert.SerializeObject(evt);
            using (var message = new ZMessage())
            {
                message.Add(new ZFrame(evt.workbook));
                message.Add(new ZFrame(data));
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
