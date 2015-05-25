using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Excel = Microsoft.Office.Interop.Excel;
using ZeroMQ;
using System.Threading;

namespace comnsense
{
    class Router
    {
        public static const string Address = "tcp://127.0.0.1:8080";
        public static const TimeSpan Interval = TimeSpan.FromMilliseconds(500);

        private ZContext ctx;
        //private ZSocket subscriber;
        //private ZSocket agent;
        private Excel.Application excel;

        public Router(ZContext ctx, Excel.Application excel)
        {
            this.ctx = ctx;
            this.excel = excel;
            //this.subscriber = new ZSocket(ctx, ZSocketType.SUB);
            //this.agent = new ZSocket(ctx, ZSocketType.DEALER);
        }

        private bool SubscriberHandler(ZSocket socket, out ZMessage message, out ZError error)
        {

            message = socket.ReceiveMessage();
            String payload = message[1].ReadString();
            this.agent.Send(new ZFrame(payload));
            error = default(ZError);
            return true;
        }

        private bool EventHandler(ZSocket socket, out ZMessage message, out ZError error)
        {
            message = socket.ReceiveMessage();
            error = null;
            return true;
        }

        private bool AsyncHandler(ZSocket socket, out ZMessage message, out ZError error)
        {
            message = socket.ReceiveMessage();
            String payload = message[0].ReadString();
            socket.Send(new ZFrame(socket.IdentityString));
            // do something with payload
            excel.ActiveSheet.Cells[1, 1] = "FUUUUUCK!";
            error = null;
            return true;
        }

        public void Run(CancellationToken ct)
        {
            using (ZSocket subscriber = new ZSocket(this.ctx, ZSocketType.PUB),
                           agent = new ZSocket(this.ctx, ZSocketType.DEALER))
            {
                subscriber.Connect(EventPublisher.Address);
                subscriber.SetOption(ZSocketOption.SUBSCRIBE, "");  // any events

                agent.SetOption(ZSocketOption.IDENTITY, System.Guid.NewGuid().ToString());
                agent.Connect(Router.Address);

                ZError error = default(ZError);
                ZMessage[] messages = null;

                ZSocket[] sockets = new ZSocket[] { 
                    subscriber, agent };

                ZPollItem[] polls = new ZPollItem[] {
                    ZPollItem.Create((ZSocket sock, out ZMessage msg, out ZError err) => {
                        msg = sock.ReceiveMessage();
                        String payload = msg[1].ReadString();
                        agent.Send(new ZFrame(payload));
                        err = default(ZError);
                        return true; 
                    }), 
                    ZPollItem.Create((ZSocket sock, out ZMessage msg, out ZError err) => {
                        error = default(ZError);
                        return true; 
                    })
                };
                try
                {
                    while (!ct.IsCancellationRequested)
                    {
                        if (!sockets.Poll(polls, ZPoll.In, ref messages, out error, Router.Interval))
                        {
                            if (error == ZError.EAGAIN)
                            {
                                Thread.Sleep(1);
                                continue;
                            }

                            if (error == ZError.ETERM)
                            {
                                break;
                            }

                            throw new ZException(error);
                        }
                    }
                }
                catch (ZException)
                {
                    if (!ct.IsCancellationRequested)
                    {
                        throw;
                    }
                }
            }
        }
    }

}
