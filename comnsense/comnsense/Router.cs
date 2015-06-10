using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Excel = Microsoft.Office.Interop.Excel;
using ZeroMQ;
using System.Threading;
using Json = Newtonsoft.Json;

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

        private Excel.Workbook GetWorkbook() 
        {
            foreach (Excel.Workbook wb in this.excel.Workbooks)
            {
                Ident id = new Ident(wb);
                if (ident == id.ToString())
                {
                    return wb;
                }
            }
            return null;
        }

        private void ApplyChange(Action action) {
            this.excel.EnableEvents = false;
            try
            {
                if (action.workbook != ident)
                {
                    return;
                }
                Excel.Workbook wb = GetWorkbook();
                foreach (Cell[] row in action.cells)
                {
                    foreach (Cell cel in row)
                    {

                    }
                }
            }
            finally
            {
                this.excel.EnableEvents = true;
            }
        }

        public void Run(CancellationToken ct)
        {
            using (ZSocket subscriber = new ZSocket(this.ctx, ZSocketType.SUB),
                           agent = new ZSocket(this.ctx, ZSocketType.DEALER))
            {
                subscriber.SetOption(ZSocketOption.SUBSCRIBE, this.ident);  // any events
                subscriber.Connect(EventPublisher.Address);

                agent.SetOption(ZSocketOption.IDENTITY, Guid.NewGuid().ToString());
                agent.Connect(Router.Address);

                ZError error = default(ZError);
                ZMessage[] messages = null;

                ZSocket[] sockets = new ZSocket[] { 
                    subscriber, agent };

                ZPollItem[] polls = new ZPollItem[] {
                    ZPollItem.Create((ZSocket sock, out ZMessage msg, out ZError err) => {
                        msg = sock.ReceiveMessage();
                        // We need the second frame
                        ZFrame frame = msg.Last();
                        String frame_str = frame.ReadString(Encoding.UTF8);
                        
                        // Sending the received frame directly
                        using (var message = new ZMessage())
                        {
                            message.Add(new ZFrame("event"));
                            message.Add(frame);
                            agent.Send(message);
                        }
                        err = default(ZError);
                        return true; 
                    }), 
                    ZPollItem.Create((ZSocket sock, out ZMessage msg, out ZError err) => {
                        msg = sock.ReceiveMessage();
                        String type = msg[0].ReadString();
                        String payload = msg[1].ReadString();
                        Action action = null;
                        try
                        {
                            action = Json.JsonConvert.DeserializeObject<Action>(
                                payload, new Json.JsonSerializerSettings { NullValueHandling = Json.NullValueHandling.Ignore });
                        }
                        catch
                        {
                            // ignore deserialization errors
                        }
                        if (action != null)
                        {
                            if (action.type == Action.ActionType.ComnsenseChange)
                            {
                                // apply change
                            }
                            if (action.type == Action.ActionType.RangeRequest)
                            {
                                // read range and send event
                            }
                        }
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
