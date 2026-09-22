#!/usr/bin/env python3
"""Build public, readable search pages from the published posts.json. Python 3 stdlib only."""
import argparse, base64, hashlib, html, json, re, shutil
from pathlib import Path
from urllib.parse import urljoin, urlsplit, quote
import xml.etree.ElementTree as ET

E=lambda s: html.escape(str(s or ''), quote=True)
def jd(v): return json.dumps(v,ensure_ascii=False).replace('<','\\u003c')
def plain(s): return re.sub(r'\s+',' ',re.sub(r'\[\[.*?\]\]','',str(s))).strip()
def safe_url(s, base):
    u=urljoin(base,str(s or ''))
    return u if urlsplit(u).scheme in ('https','http') else ''

def inline(s):
    # Only supported editor tokens produce HTML. Everything else is escaped.
    out=[]; stack=[]
    tags={'b':'strong','i':'em','u':'u','small':'small','muted':'span','byline':'small'}
    for token in re.split(r'(\[\[.*?\]\])',s):
        if token.startswith('[['):
            t=token[2:-2]
            if t in tags or re.fullmatch(r'color:#[0-9a-fA-F]{6}',t):
                key='color' if t.startswith('color:') else t
                tag=tags.get(key,'span'); style=''
                if key=='color': style=' style="color:'+t[6:]+'"'
                if key in ('muted','byline'): style=' class="muted"'
                out.append('<'+tag+style+'>');stack.append((key,tag))
            elif t.startswith('/') and stack and stack[-1][0]==t[1:]: out.append('</'+stack.pop()[1]+'>')
            else: out.append(E(token))
        else: out.append(E(token).replace('\n','<br>'))
    out.extend('</'+tag+'>' for _,tag in reversed(stack))
    return ''.join(out)

CSS='''*{box-sizing:border-box}body{margin:0;background:#0b0b0c;color:#efede7;font:17px/1.95 Pretendard,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}header,main,footer{max-width:880px;margin:auto;padding:28px 32px}header{display:flex;justify-content:space-between;gap:20px;font-size:13px}a{color:inherit;text-underline-offset:5px}h1{font-size:clamp(32px,5vw,60px);line-height:1.2;letter-spacing:-.045em;margin:50px 0 26px}h2{font-size:26px;line-height:1.5;margin:70px 0 28px}p{margin:0 0 28px;overflow-wrap:anywhere}article{background:#efeee7;color:#252525;padding:clamp(25px,6vw,70px);margin-top:36px}figure{margin:40px 0}img{display:block;max-width:100%;height:auto;margin:auto}.cover{max-height:640px;object-fit:contain}.muted,time{opacity:.66;font-size:.85em}.actions{display:flex;gap:18px;flex-wrap:wrap}.button{padding:9px 20px;border:1px solid #666;border-radius:30px;text-decoration:none}.entry{border-top:1px solid #333;padding:25px 0}.entry h2{margin:0 0 10px}hr{border:0;border-top:1px solid #ccc;margin:45px 0}footer{font-size:12px;color:#aaa}@media(max-width:600px){header,main,footer{padding:22px}article{padding:25px;font-size:16px}}'''

def build(source, output, base):
    source=Path(source).resolve(); output=Path(output).resolve();base=base.rstrip('/')+'/'
    if output==source or source in output.parents: # allow standard _site child, exclude it explicitly
        if output==source: raise ValueError('Output must differ from source')
    if not (source/'posts.json').is_file(): raise ValueError('Published posts.json is required; not generating an empty site.')
    data=json.loads((source/'posts.json').read_text()); index=(source/'index.html').read_text()
    if not isinstance(data,dict): raise ValueError('posts.json must be an object')
    seed={}
    marker='window.LK_EN_SEED='
    if marker in index: seed=json.JSONDecoder().raw_decode(index.split(marker,1)[1].lstrip())[0]
    output.mkdir(parents=True,exist_ok=True)
    # Copy existing public assets only. Never deploy repository configuration or backups.
    excluded={'.git','.github','tools','node_modules','search','_site','deliverables','upload','tests','__pycache__'}
    extensions={'.html','.css','.js','.mjs','.png','.jpg','.jpeg','.webp','.gif','.svg','.ico','.woff','.woff2','.ttf','.otf','.mp3','.mp4','.webm','.ogg','.wav','.vtt','.srt','.pdf','.xml','.txt','.json'}
    for p in source.rglob('*'):
        if not p.is_file() or p.is_symlink() or output in p.parents: continue
        rel=p.relative_to(source)
        if any(x.startswith('.') or x in excluded for x in rel.parts): continue
        if p.suffix.lower() not in extensions and rel.as_posix() not in ('posts.json','CNAME'): continue
        if p.name.lower().startswith(('readme','install','chat-proxy-worker')) or p.name in ('package.json','package-lock.json','tsconfig.json','wrangler.json','wrangler.jsonc'):continue
        target=output/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    target=output/'search'
    if target.exists(): shutil.rmtree(target)
    target.mkdir();(target/'style.css').write_text(CSS)
    urls=[]
    def asset(src):
        m=re.fullmatch(r'data:image/(png|jpeg|webp);base64,([A-Za-z0-9+/=\r\n]+)',str(src or ''))
        if m:
            raw=base64.b64decode(m[2],validate=False);name=hashlib.sha256(raw).hexdigest()[:24]+'.'+m[1]
            folder=target/'media';folder.mkdir(exist_ok=True);(folder/name).write_bytes(raw)
            return base+'search/media/'+name
        return safe_url(src,base) if src else ''
    def page(path,title,description,body,lang='ko',alternates=None,schema=None,image=None):
        url=base+path;urls.append(url)
        alt=''.join('<link rel="alternate" hreflang="'+E(k)+'" href="'+E(base+v)+'">' for k,v in (alternates or {}).items())
        nav=''.join('<a href="'+E(base+v)+'" lang="'+k+'">'+('한국어' if k=='ko' else 'English')+'</a> ' for k,v in (alternates or {}).items() if k!='x-default')
        out='<!doctype html><html lang="'+lang+'"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+E(title)+' | LOWKEY RECORDZ</title><meta name="description" content="'+E(description)+'"><link rel="canonical" href="'+E(url)+'">'+alt+'<meta property="og:title" content="'+E(title)+'"><meta property="og:description" content="'+E(description)+'"><meta property="og:url" content="'+E(url)+'"><meta property="og:type" content="'+('article' if schema and schema.get('@type')=='Article' else 'website')+'">'+('<meta property="og:image" content="'+E(image)+'">' if image else '')+'<link rel="stylesheet" href="'+base+'search/style.css">'+('<script type="application/ld+json">'+jd(schema)+'</script>' if schema else '')+'</head><body><header><a href="'+base+'">LOWKEY RECORDZ</a><nav>'+nav+'</nav></header><main>'+body+'</main><footer><a href="'+base+'search/">JOURNAL & NEWS</a> · © LOWKEY RECORDZ</footer></body></html>'
        dest=output/path/'index.html';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(out)
    entries={'ko':[],'en':[]}
    for kind,key in [('journal','journal'),('news','news'),('notice','notices')]:
        records=data.get(key,[])
        if not isinstance(records,list): raise ValueError('Invalid board '+key)
        seen=set()
        for n in records:
            id=str(n.get('id',''))
            if not re.fullmatch(r'[A-Za-z0-9_-]+',id) or id in seen: raise ValueError('Invalid/duplicate post id '+id)
            seen.add(id)
            en=(n.get('i18n') or {}).get('en',seed.get(id,{})); versions={'ko':n}
            if en.get('body') and en.get('title'): versions['en']={**n,**en}
            paths={lang:'search/'+lang+'/'+kind+'/'+id+'/' for lang in versions}
            alts={**paths,'x-default':paths['ko']}
            for lang,v in versions.items():
                title=str(v.get('title',''));body=str(v.get('body',''));images=n.get('images',[]);used=set()
                def photo(i):
                    if not 0<=i<len(images):return ''
                    used.add(i);u=asset(images[i]);return '<figure><img loading="lazy" src="'+E(u)+'" alt="'+E(title)+' — '+str(i+1)+'"></figure>' if u else ''
                # Nested inline formatting inside [[title:...]] is allowed.
                pattern=r'(\[\[title:(?:\[\[(?!title:).*?\]\]|[^\]])*\]\]|\[\[photo:\d+\]\]|\[\[page\]\]|\[\[video\]\])'
                chunks=[]
                for t in re.split(pattern,body):
                    if t.startswith('[[title:'):chunks.append('<h2>'+inline(t[8:-2])+'</h2>')
                    elif re.fullmatch(r'\[\[photo:\d+\]\]',t): chunks.append(photo(int(t[8:-2])-1))
                    elif t=='[[page]]': chunks.append('<hr>')
                    elif t=='[[video]]': pass
                    else: chunks.extend('<p>'+inline(p)+'</p>' for p in re.split(r'\n\s*\n',t) if p.strip())
                chunks.extend(photo(i) for i in range(len(images)) if i not in used)
                video=(n.get('presentation') or {}).get('video')
                if video and safe_url(video,base):chunks.append('<p><a href="'+E(safe_url(video,base))+'">'+('영상 보기' if lang=='ko' else 'Watch video')+'</a></p>')
                desc=plain(body)[:170];cover=asset(n.get('cover') or (images[0] if images else ''))
                reader=base+'?lang='+lang+'#/'+kind+'/'+quote(id)
                notice=''
                if lang=='en' and (en.get('sourceBody')!=n.get('body') or en.get('sourceTitle')!=n.get('title')):notice='<p class="muted">The Korean edition has been updated. The English revision is pending.</p>'
                schema={'@context':'https://schema.org','@type':'Article','headline':title,'description':desc,'inLanguage':lang,'mainEntityOfPage':base+paths[lang],'author':{'@type':'Organization','name':'LOWKEY RECORDZ','url':base},'publisher':{'@type':'Organization','name':'LOWKEY RECORDZ','url':base}}
                date=str(n.get('date',''))
                if re.fullmatch(r'\d{4}-\d{2}-\d{2}',date):schema['datePublished']=date
                if cover:schema['image']=[cover]
                content='<p class="muted">LOWKEY '+kind.upper()+'</p><h1>'+E(title)+'</h1><time>'+E(date)+'</time><p class="actions"><a class="button" href="'+E(reader)+'">'+(('잡지로 펼쳐 읽기' if kind=='journal' else '사이트에서 보기') if lang=='ko' else ('Open the magazine' if kind=='journal' else 'Open on website'))+'</a></p>'+notice+('<img class="cover" src="'+E(cover)+'" alt="'+E(title)+'">' if cover else '')+'<article>'+''.join(chunks)+'</article>'
                page(paths[lang],title,desc,content,lang,alts,schema,cover)
                entries[lang].append((date,paths[lang],title,kind))
    for lang in ('ko','en'):
        path='search/' if lang=='ko' else 'search/en/'
        content='<h1>JOURNAL & NEWS</h1><p>'+('로우키 레코즈의 인터뷰, 음악 이야기와 활동 소식.' if lang=='ko' else 'Interviews, music stories and updates from LOWKEY RECORDZ.')+'</p>'
        for date,p,title,kind in sorted(entries[lang],reverse=True): content+='<section class="entry"><p class="muted">'+kind.upper()+' · '+E(date)+'</p><h2><a href="'+base+p+'">'+E(title)+'</a></h2></section>'
        content+='<p><a href="'+base+'search/'+lang+'/room/">'+('비밀의 방' if lang=='ko' else 'The Secret Room')+'</a></p>'
        page(path,'LOWKEY JOURNAL & NEWS','LOWKEY RECORDZ interviews, music and news.',content,lang,{'ko':'search/','en':'search/en/','x-default':'search/'})
        title='비밀의 방' if lang=='ko' else 'The Secret Room'
        desc='카라신 주니어와 나이키 진의 음악 세계를 탐험하는 Windows XP 스타일의 웹아트. 바탕화면의 아이콘을 열고 게임과 숨겨진 이야기를 만나보세요.' if lang=='ko' else 'Explore the musical worlds of Karacin Jr. and Nike Jean in a Windows XP-inspired web artwork. Open desktop icons to discover games and hidden stories.'
        page('search/'+lang+'/room/',title,desc,'<h1>'+title+'</h1><p>'+desc+'</p><p><a class="button" href="'+base+'?lang='+lang+'#/game">'+('입장하기' if lang=='ko' else 'Enter the room')+'</a></p>',lang,{'ko':'search/ko/room/','en':'search/en/room/','x-default':'search/ko/room/'})
    ns='http://www.sitemaps.org/schemas/sitemap/0.9';ET.register_namespace('',ns);root=ET.Element('{'+ns+'}urlset')
    for url in [base]+urls: ET.SubElement(ET.SubElement(root,'{'+ns+'}url'),'{'+ns+'}loc').text=url
    ET.ElementTree(root).write(output/'sitemap.xml',encoding='utf-8',xml_declaration=True)
    (output/'.nojekyll').touch()
    # robots.txt belongs to the origin root; /web/robots.txt would not govern this site.
    print('Built',len(urls),'search pages; sitemap:',base+'sitemap.xml')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',default='.');p.add_argument('--output',default='_site');p.add_argument('--base-url',default='https://lowkeyrecordz.github.io/web/');a=p.parse_args();build(a.source,a.output,a.base_url)
