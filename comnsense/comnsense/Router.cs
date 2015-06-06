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
        public const string Address = "tcp://127.0.0.1:8888";
        public static TimeSpan Interval = TimeSpan.FromMilliseconds(500);

        private ZContext ctx;
        private String ident;
        private Excel.Application excel;

        public Router(ZContext ctx, Excel.Application excel, String ident)
        {
            this.ctx = ctx;
            this.excel = excel;
            this.ident = ident;
        }

        public void Run(CancellationToken ct)
        {
            using (ZSocket subscriber = new ZSocket(this.ctx, ZSocketType.PUB),
                           agent = new ZSocket(this.ctx, ZSocketType.DEALER))
            {
                subscriber.Connect(EventPublisher.Address);
                subscriber.SetOption(ZSocketOption.SUBSCRIBE, this.ident);  // any events

                //agent.SetOption(ZSocketOption.IDENTITY, this.ident);
                agent.Connect(Router.Address);

                ZError error = default(ZError);
                ZMessage[] messages = null;

                ZSocket[] sockets = new ZSocket[] { 
                    subscriber, agent };

                ZPollItem[] polls = new ZPollItem[] {
                    ZPollItem.Create((ZSocket sock, out ZMessage msg, out ZError err) => {
                        msg = sock.ReceiveMessage();
                        String payload = msg[1].ReadString();
                        using (var message = new ZMessage())
                        {
                            message.Add(new ZFrame(this.ident));
                            message.Add(new ZFrame(payload));
                            agent.Send(message);
                        }
                        err = default(ZError);
                        return true; 
                    }), 
                    ZPollItem.Create((ZSocket sock, out ZMessage msg, out ZError err) => {
                        msg = sock.ReceiveMessage();
                        String type = msg[0].ReadString();
                        String payload = msg[1].ReadString();
                        // deserialize action here
                        err = default(ZError);
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
