const $=x=>document.getElementById(x);
async function req(url,opt={}){const r=await fetch(url,{credentials:"include",...opt});const t=await r.text();let d;try{d=JSON.parse(t)}catch{d={raw:t}}if(!r.ok)throw Error(d.msg||"خطای درخواست");return d}
async function login(){
 $("loginMsg").textContent="در حال ورود...";
 try{
  const d=await req("/api/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({username:$("username").value,password:$("password").value})});
  if(!d.success)throw Error(d.msg||"ورود ناموفق بود");
  $("login").classList.add("hidden");$("app").classList.remove("hidden");await refresh();
 }catch(e){$("loginMsg").textContent=e.message}
}
async function refresh(){
 try{
  const [ib,cl]=await Promise.all([req("/api/inbounds/list"),req("/api/clients/list")]);
  const inbs=Array.isArray(ib.obj)?ib.obj:[];
  $("inbound").innerHTML=inbs.map(x=>`<option value="${x.id}">#${x.id} — ${x.remark||x.protocol||"Inbound"}</option>`).join("");
  const clients=Array.isArray(cl.obj)?cl.obj:[];
  $("count").textContent=clients.length;
  $("clients").textContent=clients.map(x=>`${x.email||"-"} | ${x.totalGB?Math.round(x.totalGB/1073741824)+" GB":"نامحدود"} | ${x.expiryTime?new Date(x.expiryTime).toLocaleString("fa-IR"):"نامحدود"} | ${x.enable?"فعال":"غیرفعال"}`).join("\n")||"کاربری وجود ندارد";
 }catch(e){$("clients").textContent=e.message}
}
async function createClient(){
 const name=$("name").value.trim(),gb=Number($("gb").value),days=Number($("days").value),inboundId=Number($("inbound").value);
 if(!name||gb<=0||days<=0||!inboundId){$("createMsg").textContent="همه موارد را کامل وارد کن.";return}
 $("createMsg").textContent="در حال ساخت...";
 try{
  const d=await req("/api/clients/create",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name,gb,days,inboundId})});
  $("createMsg").textContent=d.success?"کانفیگ با موفقیت ساخته شد.":(d.msg||"ساخت ناموفق بود");
  await refresh();
 }catch(e){$("createMsg").textContent=e.message}
}
