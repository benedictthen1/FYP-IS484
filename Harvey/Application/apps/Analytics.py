# Sentiment Analysis libraries
from newsapi.newsapi_client import NewsApiClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import string
from collections import Counter
import tweepy
from textblob import TextBlob
from io import BytesIO
import base64
from PIL import Image
from datetime import timedelta
from datetime import datetime

# Visualization libraries
import dash
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from pandas import DataFrame
import numpy as np
import pandas_datareader.data as web
import plotly.express as px


# News API functions: (For easier navigation and search the following)
# - Preprocessing: get_sources() & preprocessing() 
# - News table df: get_everything()
# - News bargraph df: news_top_mentioned()
# - News piechart df: news_overallsentiment()

# Twitter API functions: (For easier navigation and search the following)
# - Preprocessing: clean_txt(), clean_txt_list(), get_subjectivity(), get_sentiment(), partial_clean()
# - Twitter table df: tweet_search()
# - Twitter bargraph df: twt_top_mentioned()
# - Twitter piechart df: overallsentiment()
# - Twitter timeseries df: time_series()

# Dash visualization functions: (For easier navigation and search the following)
# - News table with sentiment coloring: generate_news_table(), quick_color()
# - Twitter table with sentiment coloring: generate_twitter_table(), quick_color()
# - News & Twitter bargraph: generate_graph()
# - News & Twitter wordcloud: generate_wordcloud()
# - Twitter piechart: generate_piechart()
# - Twitter piechart: generate_timeseries()

# Initialize Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# API calls (below)
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# In case max query for news API is hit for 1 key:
# - Phyo's newsAPI key: '127ac9edf9da4a56bbce2c6ff98978c4'
# - Harvey's newsAPI key: '28e1b77945d54b00a8c16013438a09bd'

# News API call
newsapi = NewsApiClient(api_key = '127ac9edf9da4a56bbce2c6ff98978c4')
pd.options.display.max_colwidth = 8000

# Twitter API call
consumerKey = "jfAlL4ZYSvAcLZjIghNjkPVef"
consumerSecret = "E2Wd7Fc9kQhMC4x9bTbyo8IzyDOjH7gkgXc5ZzHKBv1na0JdCB"
accessToken = "1168827517387468800-sqEsr4vVHF4ZQ0BnfyFCqTaK4H17gr"
accessTokenSecret = "FTFWWelxrVTBlwfWsHSIMe4jKI5ikzkhdZ5QcsKuCNxUS"
authenticate = tweepy.OAuthHandler(consumerKey, consumerSecret)
authenticate.set_access_token(accessToken, accessTokenSecret)
api = tweepy.API(authenticate, wait_on_rate_limit = True)

# Functions (below)
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Analytics Page dropdown fills
def get_sources():
    sources = {'source':  ['associated-press', 'australian-financial-review', 'bbc-news' , 'bloomberg', 'breitbart-news', 'business-insider',
                       'cnn', 'cbc-news', 'financial-post', 'fortune', 'google-news-uk', 'reuters', 'the-wall-street-journal', 'the-washington-post', 
                        'time', 'usa-today' ] , 'source name':  ['Associated Press', 'Australian Financial Review', 'BBC News' , 'Bloomberg', 'Breitbart News', 'Business Insider', 
                       'CNN', 'CBC News ', 'Financial Post', 'Fortune', 'Google News UK', 'Reuters', 'The Wall Street Journal', 'The Washington Post', 
                        'Time', 'USA Today' ]}
    df = pd.DataFrame(sources, columns = ['source', 'source name' ])   
    df_dict = df.to_dict('records') 
    return df_dict

# News dataframe extended cleaning labelling
def preprocessing (text):
    stopwords = nltk.corpus.stopwords.words('english')
    another = "idk,amp,aboard,about,above,gif,idk,absent,ive,weve,hes,shes,accordance,according,account,across,addition,after,against,ahead,along,alongside,also,although,amid,amidst,among,amongst,and,anent,anti,apart,around,as,aside,astride,at,athwart,atop,barring,because,before,behalf,behind,behither,below,beneath,beside,besides,between,betwixt,beyond,both,but,by,case,circa,close,concerning,considering,cum,despite,down,due,during,either,ere,even,except,excluding,failing,far,following,for,fornenst,fornent,from,front,given,if,in,including,inside,instead,into,lest,lieu,like,means,mid,minus,near,neither,next,nor,notwithstanding,of,off,on,once,only,onto,opposite,or,out,outside,outwith,over,owing,pace,past,per,place,plus,point,prior,pro,pursuant,qua,re,regard,regarding,regardless,regards,respect,round,sans,save,since,so,soon,spite,subsequent,than,thanks,that,though,through,throughout,till,times,to,top,toward,towards,under,underneath,unless,unlike,until,unto,up,upon,versus,via,vice,vis-à-vis,well,when,whenever,where,wherever,whether,while,with,within,without,worth,yet,a,able,about,across,after,all,almost,also,am,among,an,and,any,are,aren't,arent,as,at,be,because,been,but,by,can,cannot,could,dear,did,didn't,didnt,do,don't,dont,does,doesn't,doesnt,either,else,ever,every,for,from,get,got,had,has,have,he,her,hers,him,his,how,however,i,if,in,into,is,it,its,just,least,let,like,likely,may,me,might,most,must,my,neither,no,nor,not,of,off,often,on,only,or,other,our,own,rather,said,say,says,she,should,shouldn't,shouldnt,since,so,some,than,that,the,their,them,then,there,these,they,this,tis,to,too,twas,us,wants,was,wasn't,wasnt,we,were,weren't,werent,what,when,where,which,while,who,whom,why,will,with,would,yet,you,your,a's,able,about,above,according,accordingly,across,actually,after,afterwards,again,against,ain't,all,allow,allows,almost,alone,along,already,also,although,always,am,among,amongst,an,and,another,any,anybody,anyhow,anyone,anything,anyway,anyways,anywhere,apart,appear,appreciate,appropriate,are,aren't,around,as,aside,ask,asking,associated,at,available,away,awfully,be,became,because,become,becomes,becoming,been,before,beforehand,behind,being,believe,below,beside,besides,best,better,between,beyond,both,brief,but,by,c'mon,c's,came,can,can't,cannot,cant,cause,causes,certain,certainly,changes,clearly,co,com,come,comes,concerning,consequently,consider,considering,contain,containing,contains,corresponding,could,couldn't,course,currently,definitely,described,despite,did,didn't,didnt,different,do,does,doesnt,dontdoesn't,doing,don't,done,down,downwards,during,each,edu,eg,eight,either,else,elsewhere,enough,entirely,especially,et,etc,even,ever,every,everybody,everyone,everything,everywhere,ex,exactly,example,except,far,few,fifth,first,five,followed,following,follows,for,former,formerly,forth,four,from,further,furthermore,get,gets,getting,given,gives,go,goes,going,gone,got,gotten,greetings,had,hadn't,happens,hardly,has,hasn't,have,haven't,having,he,he's,hello,help,hence,her,here,here's,hereafter,hereby,herein,hereupon,hers,herself,hi,him,himself,his,hither,hopefully,how,howbeit,however,i'd,i'll,i'm,i've,ie,if,ignored,immediate,in,inasmuch,inc,indeed,indicate,indicated,indicates,inner,insofar,instead,into,inward,is,isnt,itd,itllitsisn't,it,it'd,it'll,it's,its,itself,just,keep,keeps,kept,know,knows,known,last,lately,later,latter,latterly,least,less,lest,let,let's,like,liked,likely,little,look,looking,looks,ltd,mainly,many,may,maybe,me,mean,meanwhile,merely,might,more,moreover,most,mostly,much,must,my,myself,name,namely,nd,near,nearly,need,needs,neither,never,nevertheless,new,next,nine,no,nobody,non,none,noone,nor,normally,not,nothing,novel,now,nowhere,obviously,of,off,often,oh,ok,okay,old,on,once,one,ones,only,onto,or,other,others,otherwise,ought,our,ours,ourselves,out,outside,over,overall,own,particular,particularly,per,perhaps,placed,please,plus,possible,presumably,probably,provides,que,quite,qv,rather,rd,re,really,reasonably,regarding,regardless,regards,relatively,respectively,right,said,same,saw,say,saying,says,secondly,see,seeing,seem,seemed,seeming,seems,seen,self,selves,sent,seriously,seven,several,shall,she,should,shouldn't,since,six,so,some,somebody,somehow,someone,something,sometime,sometimes,somewhat,somewhere,soon,sorry,specified,specify,specifying,still,sub,such,sup,sure,t's,take,taken,tell,tends,th,than,thank,thanks,thanx,that,that's,thats,the,their,theirs,them,themselves,then,thence,there,theres,there's,thereafter,thereby,therefore,therein,theres,thereupon,these,they,theyd,theyll,theyre,theyve,they'd,they'll,they're,they've,think,third,this,thorough,thoroughly,those,though,three,through,throughout,thru,thus,to,together,too,took,toward,towards,tried,tries,truly,try,trying,twice,two,un,under,unfortunately,unless,unlikely,until,unto,up,upon,us,use,used,useful,uses,using,usually,value,various,very,via,viz,vs,want,wants,was,wasnt,wed,well,wasn't,way,we,we'd,we'll,we're,we've,welcome,well,went,were,werent,whats,weren't,what,what's,whatever,when,whence,whenever,where,where's,whereafter,whereas,whereby,wherein,whereupon,wherever,whether,which,while,whither,who,who's,whoever,whole,whom,whose,why,will,willing,wish,with,within,without,won't,wonder,would,would,wouldn't,yes,yet,you,you'd,you'll,you're,you've,your,yours,yourself,yourselves,zero,reuters,ap,jan,feb,mar,apr,may,jun,jul,aug,sep,oct,nov,dec,tech,news,index,mon,tue,wed,thu,fri,sat,'s,a,a's,able,about,above,according,accordingly,across,actually,after,afterwards,again,against,ain't,all,allow,allows,almost,alone,along,already,also,although,always,am,amid,among,amongst,an,and,another,any,anybody,anyhow,anyone,anything,anyway,anyways,anywhere,apart,appear,appreciate,appropriate,are,aren't,around,as,aside,ask,asking,associated,at,available,away,awfully,b,be,became,because,become,becomes,becoming,been,before,beforehand,behind,being,believe,below,beside,besides,best,better,between,beyond,both,brief,but,by,c,c'mon,c's,came,can,can't,cannot,cant,cause,causes,certain,certainly,changes,clearly,co,com,come,comes,concerning,consequently,consider,considering,contain,containing,contains,corresponding,could,couldn't,course,currently,d,definitely,described,despite,did,didn't,different,do,does,doesn't,doing,don't,done,down,downwards,during,e,each,edu,eg,e.g.,eight,either,else,elsewhere,enough,entirely,especially,et,etc,etc.,even,ever,every,everybody,everyone,everything,everywhere,ex,exactly,example,except,f,far,few,fifth,five,followed,following,follows,for,former,formerly,forth,four,from,further,furthermore,g,get,gets,getting,given,gives,go,goes,going,gone,got,gotten,greetings,h,had,hadn't,happens,hardly,has,hasn't,have,haven't,having,he,he's,hello,help,hence,her,here,here's,hereafter,hereby,herein,hereupon,hers,herself,hi,him,himself,his,hither,hopefully,how,howbeit,however,i,i'd,i'll,i'm,i've,ie,i.e.,if,ignored,immediate,in,inasmuch,inc,indeed,indicate,indicated,indicates,inner,insofar,instead,into,inward,is,isn't,it,it'd,it'll,it's,its,itself,j,just,k,keep,keeps,kept,know,knows,known,l,lately,later,latter,latterly,least,less,lest,let,let's,like,liked,likely,little,look,looking,looks,ltd,m,mainly,many,may,maybe,me,mean,meanwhile,merely,might,more,moreover,most,mostly,mr.,ms.,much,must,my,myself,n,namely,nd,near,nearly,necessary,need,needs,neither,never,nevertheless,new,next,nine,no,nobody,non,none,noone,nor,normally,not,nothing,novel,now,nowhere,o,obviously,of,off,often,oh,ok,okay,old,on,once,one,ones,only,onto,or,other,others,otherwise,ought,our,ours,ourselves,out,outside,over,overall,own,p,particular,particularly,per,perhaps,placed,please,plus,possible,presumably,probably,provides,q,que,quite,qv,r,rather,rd,re,really,reasonably,regarding,regardless,regards,relatively,respectively,right,s,said,same,saw,say,saying,says,second,secondly,see,seeing,seem,seemed,seeming,seems,seen,self,selves,sensible,sent,serious,seriously,seven,several,shall,she,should,shouldn't,since,six,so,some,somebody,somehow,someone,something,sometime,sometimes,somewhat,somewhere,soon,sorry,specified,specify,specifying,still,sub,such,sup,sure,t,t's,take,taken,tell,tends,th,than,thank,thanks,thanx,that,that's,thats,the,their,theirs,them,themselves,then,thence,there,there's,thereafter,thereby,therefore,therein,theres,thereupon,these,they,they'd,they'll,they're,they've,think,third,this,thorough,thoroughly,those,though,three,through,throughout,thru,thus,to,together,too,took,toward,towards,tried,tries,truly,try,trying,twice,two,u,un,under,unfortunately,unless,unlikely,until,unto,up,upon,us,use,used,useful,uses,using,usually,uucp,v,value,various,very,via,viz,vs,w,want,wants,was,wasn't,way,we,we'd,we'll,we're,we've,welcome,well,went,were,weren't,what,what's,whatever,when,whence,whenever,where,where's,whereafter,whereas,whereby,wherein,whereupon,wherever,whether,which,while,whither,who,who's,whoever,whole,whom,whose,why,will,willing,wish,with,within,without,won't,wonder,would,would,wouldn't,x,y,yes,yet,you,you'd,you'll,you're,you've,your,yours,yourself,yourselves,z,zero,.com,.ly,.net,.org,aahh,aarrgghh,abt,ftl,ftw,fu,fuck,fucks,gtfo,gtg,haa,hah,hahah,haha,hahaha,hahahaha,hehe,heh,hehehe,hi,hihi,hihihi,http,https,huge,huh,huhu,huhuhu,idk,iirc,im,imho,imo,ini,irl,ish,isn,isnt,j/k,jk,jus,just,justwit,juz,kinda,kthx,kthxbai,kyou,laa,laaa,lah,lanuch,leavg,leh,lol,lols,ltd,mph,mrt,msg,msgs,muahahahahaha,nb,neways,ni,nice,pls,plz,plzz,psd,pte,pwm,pwned,qfmft,qft,tis,tm,tmr,tyty,tyvm,um,umm,viv,vn,vote,voted,w00t,wa,wadever,wah,wasn,wasnt,wassup,wat,watcha,wateva,watever,watnot,wats,wayy,wb,weren,werent,whaha,wham,whammy,whaow,whatcha,whatev,whateva,whatevar,whatever,whatnot,whats,whatsoever,whatz,whee,whenz,whey,whore,whores,whoring,win,wo,woah,woh,wooohooo,woot,wow,wrt,wtb,wtf,wth,wts,wtt,www,xs,ya,yaah,yah,yahh,yahoocurrency,yall,yar,yay,yea,yeah,yeahh,yeh,yhoo,ymmv,young,youre,yr,yum,yummy,yumyum,yw,zomg,zz,zzz,loz,lor,loh,tsk,meh,lmao,wanna,doesn,liao,didn,didnt,omg,ohh,ohgod,hoh,hoo,bye,byee,byeee,byeeee,lmaolmao,yeah,yeahh,yeahhh,yeahhhh,yeahhhhh,yup,yupp,hahahahahahaha,hahahahahah,hahhaha,wooohoooo,wahaha,haah,2moro,veh,noo,nooo,noooo,hahas,ooooo,ahahaha,ahahahahah,tomolow,.com,.ly,.net,.org,aahh,aarrgghh,abt,accent,accented,accents,acne,ads,afaik,aft,ago,ahead,ain,aint,aircon,alot,am,annoy,annoyed,annoys,anycase,anymore,app,apparently,apps,argh,ass,asses,awesome,babeh,bad,bai,based,bcos,bcoz,bday,bit,biz,blah,bleh,bless,blessed,blk,blogcatalog,bro,bros,btw,byee,com,congrats,contd,conv,cos,cost,costs,couldn,couldnt,cove,coves,coz,crap,cum,curnews,curr,cuz,dat,de,didn,didnt,diff,dis,doc,doesn,doesnt,don,dont,dr,dreamt,drs,due,dun,dunno,duper,eh,ehh,emo,emos,eng,esp,fadein,ffs,fml,frm,ftl,ftw,fu,fuck,fucks,fwah,g2g,gajshost,gd,geez,gg,gigs,gtfo,gtg,haa,haha,hahaha,hasn,hasnt,hav,haven,havent,hee,heh,hehe,hehehe,hello,hey,hi,hmm,ho,hohoho,http,https,huh,huhu,huhuhu,idk,iirc,im,imho,imo,info,ini,irl,ish,isn,isnt,issued,j/k,jk,jus,just,justwit,juz,kinda,kthx,kthxbai,kyou,laa,laaa,lah,lanuch,lawl,leavg,leh,lfg,lfm,ll,lmao,lmfao,lnks,lol,lols,lotsa,lotta,ltd,luv,ly,macdailynews,meh,mph,msg,msgs,muahahahahaha,nb,neato,ni,nite,nom,noscript,nvr,nw,ohayo,omfg,omfgwtf,omg,omgwtfbbq,omw,org,pf,pic,pls,plz,plzz,pm,pmsing,ppl,pre,pro,psd,pte,pwm,pwned,qfmft,qft,rawr,rawrr,rofl,roflmao,rss,rt,sec,secs,seem,seemed,seems,sgreinfo,shd,shit,shits,shitz,shld,shouldn,shouldnt,shudder,sq,sqft,sqm,srsly,stfu,stks,su,suck,sucked,sucks,suckz,sux,swf,tart,tat,tgif,thanky,thk,thks,tht,tired,tis,tm,tmr,tsk,ttyl,ty,tym,tyme,typed,tyty,tyvm,um,umm,va,valid,valids,var,vc,ve,viv,vn,w00t,wa,wadever,wah,wasn,wasnt,wassup,wat,watcha,wateva,watnot,wats,wayy,wb,web,website,websites,weren,werent,whaha,wham,whammy,whaow,whatcha,whatev,whateva,whatevar,whatever,whatnot,whats,whatsoever,whatz,whee,whenz,whey,whore,whores,whoring,wo,woah,woh,wooohooo,woot,wow,wrt,wtb,wtf,wth,wts,wtt,www,xs,ya,yaah,yah,yahh,yahoocurrency,yall,yar,yay,yea,yeah,yeahh,year,yearly,years,yeh,yhoo,ymmv,young,youre,yr,yum,yummy,yumyum,yw,zomg,zz,zzz,fucking,mrs,mr,eh,ehh,ehhh,lot,lots,http,html,com,ly,net,org,hahahahahahahahaha,hahahahaha,hahahahah,zzzzz,#teamfollowback,#teamfollow,#follow,#autofollow,#followgain,#followbackk,#teamautofollow,#followme,#ifollow,#followngain,#followback,#followfriday,#ifollowback,#200aday,#500aday,#1000aday,hahahahha,lolololol,lololol,lolol,lol,dude,hmmm,humm,tumblr,kkkk,fk,yayyyyyy,fffffffuuuuuuuuuuuu,zzzz,zzzzz,noooooooooo,noo,nooo,noooo,hahahhaha,woohoo,lalalalalalala,lala,lalala,lalalala,whahahaahahahahahah,.com,.ly,.net,.org,aahh,aarrgghh,abt,ftl,ftw,fu,fuck,fucks,gtfo,gtg,haa,hah,hahah,haha,hahaha,hahahaha,hehe,heh,hehehe,hi,hihi,hihihi,http,https,huge,huh,huhu,huhuhu,idk,iirc,im,imho,imo,ini,irl,ish,isn,isnt,j/k,jk,jus,just,justwit,juz,kinda,kthx,kthxbai,kyou,laa,laaa,lah,lanuch,leavg,leh,lol,lols,ltd,mph,mrt,msg,msgs,muahahahahaha,nb,neways,ni,nice,pls,plz,plzz,psd,pte,pwm,pwned,qfmft,qft,tis,tm,tmr,tyty,tyvm,um,umm,viv,vn,vote,voted,w00t,wa,wadever,wah,wasn,wasnt,wassup,wat,watcha,wateva,watever,watnot,wats,wayy,wb,weren,werent,whaha,wham,whammy,whaow,whatcha,whatev,whateva,whatevar,whatever,whatnot,whats,whatsoever,whatz,whee,whenz,whey,whore,whores,whoring,win,wo,woah,woh,wooohooo,woot,wow,wrt,wtb,wtf,wth,wts,wtt,www,xs,ya,yaah,yah,yahh,yahoocurrency,yall,yar,yay,yea,yeah,yeahh,yeh,yhoo,ymmv,young,youre,yr,yum,yummy,yumyum,yw,zomg,zz,zzz,loz,lor,loh,tsk,meh,lmao,wanna,doesn,liao,didn,didnt,omg,ohh,ohgod,hoh,hoo,bye,byee,byeee,byeeee,lmaolmao,yeah,yeahh,yeahhh,yeahhhh,yeahhhhh,yup,yupp,hahahahahahaha,hahahahahah,hahhaha,wooohoooo,wahaha,haah,2moro,veh,noo,nooo,noooo,hahas,ooooo,ahahaha,ahahahahah,tomolow,.com,.ly,.net,.org,aahh,aarrgghh,abt,accent,accented,accents,acne,ads,afaik,aft,ago,ahead,ain,aint,aircon,alot,am,annoy,annoyed,annoys,anycase,anymore,app,apparently,apps,argh,ass,asses,awesome,babeh,bad,bai,based,bcos,bcoz,bday,big,bigger,biggest,bit,biz,blah,bleh,bless,blessed,blk,blogcatalog,bored,boring,bright,bring,brings,bro,broke,broken,bros,brought,btw,bye,byebye,byee,cheap,clutter,cluttered,com,common,complete,completed,completes,completing,congrats,congratulation,congratulations,consecutive,consecutively,contd,continue,continues,conv,cos,cost,costs,couldn,couldnt,cove,coves,coz,crap,crappy,crazy,crowded,cum,curnews,curr,cute,cuties,cuz,daily,damn,dark,dat,days,de,dear,didn,didnt,diff,dis,distracted,distracts,doc,doesn,doesnt,don,dont,door,doors,double,doubled,doubles,dr,dreamt,drs,due,dun,dunno,duper,earlier,earliest,early,earn,earned,earns,easier,easy,eat,eaten,eats,eh,ehh,emo,emos,enable,enables,enabling,eng,enter,entered,enters,esp,everyday,everywhere,exclude,excluded,excludes,excuse,excused,excuses,explode,exploded,explodes,eye,eyes,fadein,fail,failed,fails,fake,fall,falls,false,famous,fast,faster,fastest,fat,featured,feel,feeling,feels,fell,felt,ffs,finally,find,finds,finish,finished,flat,flats,flight,flights,fml,follow,followed,follows,food,form,formed,forming,forms,found,free,fries,frm,ftl,ftw,fu,fuck,fucks,full,fully,fun,funny,furnish,furnished,future,fwah,g2g,gajshost,gave,gd,geez,gg,gigs,gimme,give,giveaway,giveaways,given,gives,gonna,good,goodbye,goodnight,got,gotta,grats,gratz,great,greats,gtfo,gtg,guess,guessing,haa,haha,hahaha,happen,happened,happens,hard,harder,hardest,hasn,hasnt,hate,hated,hates,hav,haven,havent,hdb,hear,heard,hears,heart,hee,heh,hehe,hehehe,hello,hey,hi,highest,hmm,ho,hohoho,hopefully,hoping,host,hosted,hosts,hot,hour,hours,http,https,huge,huh,huhu,huhuhu,hurt,hurts,idiot,idiots,idk,iirc,im,imho,imo,important,indicate,indicated,indicates,indicating,info,ini,install,interact,interacted,interacting,interacts,interested,interesting,involve,involved,involves,irl,ish,isn,isnt,issued,j/k,jk,jus,just,justwit,juz,kill,killed,kills,kinda,kthx,kthxbai,kyou,laa,laaa,lah,lanuch,last,late,later,latest,laugh,laughed,laughs,launched,launches,lawl,learn,learned,learns,leavg,leh,lend,lender,lenders,lfg,lfm,lightly,like,liked,likes,lined,listed,listen,listened,listening,listens,live,lived,ll,lmao,lmfao,lnks,loaned,local,locate,located,locates,lock,locked,locks,lol,lols,look,looked,looking,looks,lose,loss,lot,lotsa,lotta,love,loved,loves,lowest,ltd,luv,ly,macdailynews,mad,made,mailed,main,make,makes,manage,managed,manages,march,may,mean,means,mee,meet,meets,meh,mention,mentioned,mentions,met,million,millions,min,mine,mini,mins,miss,missed,misses,mix,mixed,mixes,monthly,mph,mrt,msg,msgs,muahahahahaha,mum,named,national,nb,neato,negotiable,net,neways,newly,news,ni,nice,night,nite,nom,noscript,notice,notices,noticing,notified,notifies,notify,now,nowadays,nvr,nw,obvious,obviously,occur,occured,occurs,october,office,offices,ohayo,old,omfg,omfgwtf,omg,omgwtfbbq,omw,online,only,open,opened,opens,opportunities,opportunity,order,ordered,ordering,orders,org,organize,organized,organizes,pack,packed,packs,paid,pain,painful,painless,pains,pair,park,parks,passed,past,pay,pays,pf,phew,phone,phones,pic,pick,picked,picks,pics,pictures,pig,pigs,pissed,place,places,play,played,plays,pls,plz,plzz,pm,pmsing,post,posted,posts,powerful,ppl,pre,prefer,present,presented,presents,pretty,preview,previewed,previews,previous,priced,primary,private,pro,produce,produced,produces,prolly,prosperous,provide,provided,provides,psd,pte,purchase,purchased,purchases,pwm,pwned,qfmft,qft,quality,quick,ran,rate,rated,rawr,rawrr,reader,readers,real,realise,realised,realises,realize,realized,realizes,receive,received,receives,recent,recently,recommend,recommended,recommends,recover,recovered,recovers,refuse,refused,refuses,regular,rejoice,relate,related,relates,remember,remembered,remembers,remind,reminded,reminds,remove,removed,removes,rename,renamed,renames,rent,rental,rented,rents,replace,replaced,replaces,replied,replies,reply,reported,reports,requested,require,required,requires,resort,resorts,resulted,return,returned,returns,review,reviewed,reviews,right,rightaway,rofl,roflmao,rss,rt,run,runs,safe,safety,sale,sales,sang,save,saved,saves,scratch,scratched,scratches,screwed,screws,search,searched,searches,sec,secondary,secs,seem,seemed,seems,select,selected,selecting,selects,sell,sells,send,sends,sent,serve,served,serves,set,sets,settle,settled,settles,sg,sgd,sgreinfo,share,shared,shares,shd,shit,shits,shitz,shld,shortest,shouldn,shouldnt,show,showed,shown,shows,shudder,sick,sicks,side,sides,signed,significant,significantly,similar,similars,sing,singaporestd,single,singled,singles,sings,site,sites,skin,sleep,sleeps,slept,slight,slightly,slipped,slow,small,sms,soba,soft,sold,somemore,soon,sore,sores,sound,sounded,sounds,soup,soups,source,sources,special,specials,specific,specifically,spend,spending,spends,spent,spot,spots,sq,sqft,sqm,srsly,start,started,starts,stay,stayed,stays,stfu,stks,stop,stopped,stops,stories,story,strong,student,students,studied,studies,study,stuff,stupid,stupids,su,suck,sucked,sucks,suckz,sue,sued,sues,sunday,sundays,sung,support,supported,supporting,supports,sux,sweet,swf,sync,take,takes,taking,talk,talked,talks,tallest,target,targets,tart,tat,taught,tbh,tbl,teach,teaches,teehee,tel,tells,tgif,thank,thanks,thanky,theme,themes,thing,things,think,thinks,thk,thks,tht,tired,tis,tm,tmr,today,toilet,toilets,told,tomorrow,tonight,took,total,totals,treat,treated,treats,tree,trees,true,tsk,ttyl,turned,turns,twittering,ty,tym,tyme,typed,tyty,tyvm,um,umm,unit,units,update,updated,updates,upgrade,upgraded,upgrades,upload,uploaded,uploads,va,valid,valids,var,vc,ve,visit,visited,visits,viv,vn,w00t,wa,wadever,wah,wait,waited,waiting,waits,wanna,want,wanted,wants,wasn,wasnt,wassup,wat,watch,watcha,watched,watches,watching,wateva,watever,watnot,wats,wayy,wb,web,website,websites,wednesday,week,weekly,weeks,weird,weren,werent,whaha,wham,whammy,whaow,whatcha,whatev,whateva,whatevar,whatever,whatnot,whats,whatsoever,whatz,whee,whenz,whey,white,whore,whores,whoring,win,wins,wish,wished,wishes,wo,woah,woh,woman,women,womens,won,wonder,wondered,wondering,wonders,wooohooo,woot,word,words,work,working,works,world,worlds,worse,worst,wow,write,writes,written,wrong,wrote,wrt,wtb,wtf,wth,wts,wtt,www,xs,ya,yaah,yah,yahh,yahoocurrency,yall,yar,yay,yea,yeah,yeahh,year,yearly,years,yeh,yhoo,ymmv,young,youre,yr,yum,yummy,yumyum,yw,zomg,zz,zzz,girl,girls,boy,boys,man,men,mens,mans,guy,guys,fucking,mrs,mr,miss,eh,ehh,ehhh,lot,lots,http,html,com,ly,net,org,hahahahahahahahaha,hahahahaha,first,second,third,1st,2nd,3rd,hahahahah,zzzzz,#teamfollowback,#teamfollow,#follow,#autofollow,#followgain,#followbackk,#teamautofollow,#followme,#ifollow,#followngain,#followback,#followfriday,#ifollowback,tweet,tweets,#200aday,#500aday,#1000aday,thing,things,think,thinks,thinking,hahahahha,lolololol,lololol,lolol,lol,dude,hmmm,humm,tumblr,morning,noon,afternoon,today,evening,birthday,birthdays,kkkk,fk,yayyyyyy,fffffffuuuuuuuuuuuu,zzzz,zzzzz,noooooooooo,noo,nooo,noooo,hahahhaha,#ff,#followback,#teamfollowback,#f4f,#autofollow,#500aday,#instantfollowback,#autofollowback,#1000aday,#ifollowback,#teamautofollow,#f4f,#instantfollow,#autofollow,.com,.ly,.net,.org,aahh,aarrgghh,abt,accent,accented,accents,account,accounts,acne,activities,activity,ad,add,added,adding,adds,admission,admissions,ads,afaik,affiliate,affiliates,affirmation,affirmations,aft,afternoon,ago,ahead,ain,aint,aircon,album,albums,allergies,allergy,allow,allowed,allows,alot,am,angry,announcement,announcements,annoy,annoyed,annoys,anycase,anymore,app,apparently,approve,approved,approves,apps,april,area,areas,argh,arrive,arrived,arrives,article,articles,asia,asian,ask,asked,asks,ass,asses,ate,attempt,attempting,attempts,attend,attended,attends,august,auto,autoindustry,awesome,babeh,babies,baby,back,backed,bad,bag,bags,bai,balance,bank,banks,based,bcos,bcoz,bday,bed,bedroom,belong,belonged,belongs,big,bigger,biggest,billion,billons,birthday,birthdays,bit,biz,blah,bleh,bless,blessed,blk,blog,blogcatalog,blogger,bloggers,blogging,blogs,bloody,book,bored,boring,bottle,bottles,bought,box,boxes,boy,boys,break,breakfast,breakfasts,bright,bring,brings,bro,broke,broken,bros,brought,btw,build,builds,built,bus,buses,butter,buy,buys,bye,byebye,byee,call,called,calls,cancel,canceled,cancelled,cancels,candies,candy,car,career,careers,cars,catch,catches,caught,change,changed,changes,changing,channel,channels,cheap,check,checked,checks,chicken,chickens,chocolate,chocolates,choice,choices,class,classes,click,close,closed,closes,cloth,clothe,clothes,clutter,cluttered,cna,coffee,com,comeback,comment,commenting,comments,common,companies,company,complete,completed,completes,completing,conditions,condo,condominium,condominoums,condos,congrats,congratulation,congratulations,consecutive,consecutively,consult,consultant,consults,contact,contacted,contacts,contd,content,contents,continue,continues,conv,cookies,cos,cost,costs,couldn,couldnt,countries,country,couple,couples,course,courses,cove,coves,coz,crap,crappy,crazy,cream,create,created,creates,creats,crowded,cum,curnews,curr,customer,customers,cute,cuties,cuz,dad,daily,damn,dark,dat,date,dated,dates,day,days,de,dead,dear,death,december,depend,depended,depends,deposit,deposited,deposits,detail,details,didn,didnt,die,died,dies,diff,dinner,dinners,dis,distract,distracted,distracts,doc,docs,document,documents,doesn,doesnt,don,dont,door,doors,double,doubled,doubles,download,downloads,dr,dreamt,drs,due,dun,dunno,duper,earlier,earliest,early,earn,earned,earns,easier,easy,eat,eaten,eats,eh,ehh,email,emails,emo,emos,enable,enables,enabling,end,ends,eng,enter,entered,enters,esp,event,events,everyday,everywhere,exclude,excluded,excludes,excuse,excused,excuses,explode,exploded,explodes,eye,eyes,fadein,fail,failed,fails,fake,fall,falls,false,families,family,famous,fast,faster,fastest,fat,favorite,favorited,favorites,favourite,favourites,featured,february,feed,feeds,feel,feeling,feels,fell,felt,female,females,ffs,finally,find,finds,finish,finished,flat,flats,flight,flights,fml,follow,followed,follows,food,form,formed,forming,forms,found,free,friday,friend,friends,fries,frm,fruit,fruits,ftl,ftw,fu,fuck,fucks,full,fully,fun,funny,furnish,furnished,future,fwah,g2g,gajshost,gave,gd,geez,gg,gift,gifted,gifts,gigs,gimme,girl,girls,give,giveaway,giveaways,given,gives,gonna,good,goodbye,goodnight,got,gotta,grats,gratz,great,greats,gtfo,gtg,guess,guessing,guy,guys,haa,haha,hahaha,hair,hairs,hand,hands,happen,happened,happens,hard,harder,hardest,hasn,hasnt,hate,hated,hates,hav,haven,havent,hdb,hear,heard,hears,heart,hee,heh,hehe,hehehe,hello,hey,hi,highest,hmm,ho,hohoho,holiday,holidays,home,homework,homeworks,hope,hopefully,hoping,host,hosted,hosts,hot,hour,hours,http,https,huge,huh,huhu,huhuhu,hurt,hurts,idea,ideas,idiot,idiots,idk,iirc,im,imho,imo,important,indicate,indicated,indicates,indicating,info,information,ini,install,installation,installations,installs,interact,interacted,interacting,interaction,interactions,interacts,interested,interesting,internet,introduction,introductions,involve,involved,involves,irl,ish,isn,isnt,issue,issued,issues,item,items,j/k,january,jk,job,jobs,july,june,jus,just,justwit,juz,key,keys,kid,kids,kill,killed,kills,kinda,kthx,kthxbai,kyou,laa,laaa,lah,lanuch,last,late,later,latest,laugh,laughed,laughs,launched,launches,lawl,learn,learned,learns,leavg,leh,lend,lender,lenders,lfg,lfm,life,light,lightly,lights,like,liked,likes,line,lined,lines,link,links,listed,listen,listened,listening,listens,live,lived,lives,ll,lmao,lmfao,lnks,loaned,local,locate,located,locates,location,locations,lock,locked,locks,lol,lols,look,looked,looking,looks,lose,loss,lot,lotsa,lotta,love,loved,loves,lowest,ltd,lunch,lunches,luv,ly,macdailynews,mad,made,mailed,main,make,makes,male,males,man,manage,managed,manages,march,may,mean,means,media,medias,mee,meet,meets,meh,men,mens,mention,mentioned,mentions,menu,menus,merry,message,messages,met,million,millions,min,mine,mini,mins,minute,minutes,miss,missed,misses,mix,mixed,mixes,mom,monday,money,month,monthly,months,morning,movie,movies,mph,mrt,msg,msgs,muahahahahaha,mum,mushroom,music,musics,named,national,nb,neato,negotiable,net,neways,newly,news,ni,nice,night,nite,nom,noodle,noodles,noscript,notes,notice,notices,noticing,notified,notifies,notify,november,now,nowadays,nvr,nw,obvious,obviously,occur,occured,occurs,october,office,offices,ohayo,old,omfg,omfgwtf,omg,omgwtfbbq,omw,online,only,open,opened,opens,opportunities,opportunity,order,ordered,ordering,orders,org,organize,organized,organizes,pack,packed,packs,page,pages,paid,pain,painful,painless,pains,pair,parent,parents,park,parks,passed,past,pay,pays,people,person,pf,phew,phone,phones,photo,photos,pic,pick,picked,picks,pics,pictures,pig,pigs,pissed,place,places,play,played,plays,pls,plz,plzz,pm,pmsing,post,posted,posts,powerful,ppl,pre,prefer,present,presentation,presentations,presented,presents,pretty,preview,previewed,previews,previous,price,priced,prices,primary,private,pro,problem,problems,produce,produced,produces,product,production,productions,products,profile,profiles,programs,project,projects,prolly,prosperous,provide,provided,provides,psd,pte,public,purchase,purchased,purchases,pwm,pwned,qfmft,qft,quality,quick,ran,rate,rated,rawr,rawrr,reader,readers,real,realise,realised,realises,realize,realized,realizes,receive,received,receives,recent,recently,recommend,recommended,recommends,recover,recovered,recovers,refuse,refused,refuses,regular,rejoice,relate,related,relates,remember,remembered,remembers,remind,reminded,reminds,remove,removed,removes,rename,renamed,renames,rent,rental,rented,rents,replace,replaced,replaces,replied,replies,reply,report,reported,reports,request,requested,requests,require,required,requires,resort,resorts,result,resulted,results,return,returned,returns,retweet,retweets,review,reviewed,reviews,rice,right,rightaway,road,roads,rocks,rofl,roflmao,role,roles,room,rooms,rss,rt,run,runs,safe,safety,sale,sales,sang,saturday,save,saved,saves,scratch,scratched,scratches,screen,screened,screens,screwed,screws,search,searched,searches,season,seasons,sec,secondary,secs,seem,seemed,seems,select,selected,selecting,selects,sell,sells,send,sends,sent,september,serve,served,serves,service,services,set,sets,settle,settled,settles,sg,sgd,sgreinfo,share,shared,shares,shd,shit,shits,shitz,shld,shoe,shoes,shop,shops,shortest,shouldn,shouldnt,show,showed,shown,shows,shudder,sick,sicks,side,sides,signed,significant,significantly,similar,similars,sing,singapore,singaporestd,single,singled,singles,sings,site,sites,skin,sleep,sleeps,slept,slight,slightly,slipped,slow,small,sms,soba,soft,sold,somemore,son,sons,soon,sore,sores,sound,sounded,sounds,soup,soups,source,sources,special,specials,specific,specifically,spend,spending,spends,spent,spot,spots,sq,sqft,sqm,srsly,start,started,starts,stay,stayed,stays,stfu,stks,stop,stopped,stops,stories,story,strong,student,students,studied,studies,study,stuff,stupid,stupids,su,suck,sucked,sucks,suckz,sue,sued,sues,sunday,sundays,sung,support,supported,supporting,supports,sux,sweet,swf,sync,take,takes,taking,talk,talked,talks,tallest,target,targets,tart,tat,taught,tbh,tbl,tea,teach,teacher,teachers,teaches,teehee,tel,tells,tgif,thank,thanks,thanky,theme,themes,thing,things,think,thinks,thk,thks,thought,throat,throats,tht,thursday,ticket,tickets,time,tips,tired,tis,tm,tmr,today,toilet,toilets,told,tomorrow,tonight,took,total,totals,treat,treated,treats,tree,trees,true,tsk,ttyl,tuesday,turn,turned,turns,tweet,tweeting,tweets,twittering,ty,tym,tyme,type,typed,types,tyty,tyvm,um,umm,unit,units,update,updated,updates,upgrade,upgraded,upgrades,upload,uploaded,uploads,url,urls,usb,usd,user,users,va,valid,valids,var,vc,ve,version,versions,video,videos,visit,visited,visits,viv,vn,vote,voted,votes,w00t,wa,wadever,wah,wait,waited,waiting,waits,wanna,want,wanted,wants,wasn,wasnt,wassup,wat,watch,watcha,watched,watches,watching,wateva,watever,watnot,wats,wayy,wb,web,website,websites,wednesday,week,weekly,weeks,weird,weren,werent,whaha,wham,whammy,whaow,whatcha,whatev,whateva,whatevar,whatever,whatnot,whats,whatsoever,whatz,whee,whenz,whey,white,whore,whores,whoring,win,wins,wish,wished,wishes,wo,woah,woh,woman,women,womens,won,wonder,wondered,wondering,wonders,wooohooo,woot,word,words,work,working,works,world,worlds,worse,worst,wow,write,writes,written,wrong,wrote,wrt,wtb,wtf,wth,wts,wtt,www,xs,ya,yaah,yah,yahh,yahoocurrency,yall,yar,yay,yea,yeah,yeahh,year,yearly,years,yeh,yesterday,yhoo,ymmv,young,youre,yr,yum,yummy,yumyum,yw,zomg,zz,zzz"
    additional = another.split(",")
    stopwords += additional 
    stemmer = SnowballStemmer("english")
    tokens = re.split('\W+', text)
    result = [word for word in tokens if word not in stopwords]       
    return result

# News table dataframe creation
def get_everything(query, source):

    data = newsapi.get_everything(q = query, sources = source, language = 'en', sort_by = 'relevancy' , page_size = 100) 
    df = pd.DataFrame(data['articles'])  

    df['description'].fillna(value="stop", inplace=True)
    # None value handling for Description & urlToImage columns
    df['clean_description'] =  df['description'].apply(lambda x: preprocessing(x.lower()))
    df['urlToImage'].fillna(value="http://www.trinityschool.org.uk/wp-content/uploads/2013/03/News.jpg", inplace=True)

    senti_score = []
    result = []
    
    for index, row in df.iterrows():

        published_at = row['publishedAt'].split('T')[0]
        row['publishedAt'] = published_at.replace("-", "/")

        analyzer = SentimentIntensityAnalyzer()
        vs = analyzer.polarity_scores(row['description'])
        compound = vs.get('compound') 
        senti_score.append(compound) 
        
        if compound >= 0.05:
            result.append('Positive')
        elif compound <= -0.2:
            result.append('Negative')
        else:
            result.append('Neutral') 

    df['sentiment'] = result
    df['date'] = df['publishedAt']

    return df

# News bargraph dataframe creation
def news_top_mentioned(df,query):
    word_list = []
    for index, rows in df.iterrows():
        for each_word in rows.clean_description:
            if each_word not in word_list:
                if len(str(each_word)) > 3 and each_word != query:
                    word_list.append(" " + str(each_word) + " ")                     

    counts = dict()
    for word in word_list:
        if word in counts:
            counts[word] += 1
        else:
            counts[word] = 1
            
    df = pd.DataFrame(list(counts.items()),columns = ['word','count'])
    df = df.sort_values(by ='count' , ascending=False)
    return df

# News piechart dataframe creation
def news_overallsentiment(df):

    #get the percentage of positive tweets
    postnews = df[df.sentiment == 'Positive']
    postnews = postnews['description']
    
    # get the percentage of negative tweets
    negnews = df[df.sentiment == 'Negative']
    negnews = negnews['description']
    
    #get the percentage of neutral tweets
    neunews = df[df.sentiment == 'Neutral']
    neunews = neunews['description']
    
    articles = {'Sentiment': ['Positive','Negative','Neutral'],
        'Overall Score': [round((postnews.shape[0] / df.shape[0]) *100, 1),round( (negnews.shape[0] / df.shape[0] * 100) , 1), round( (neunews.shape[0] / df.shape[0] * 100) , 1)]
        }
    df = pd.DataFrame(articles, columns = ['Sentiment', 'Overall Score'])
    
    return df

# Twitter dataframe extended cleaning labelling
def clean_txt(text):  
    
    text = re.sub(r'@[A-Za-z0-9]+', '', text)
    text = re.sub(r'RT[\s]+', '',  text) # removing RT
    text = re.sub(r'https?:\/\/\S+', '', text) #Remove the hyper link
    text = text.replace('\n','')
    text = text.replace(':','')
        
    return text

# Twitter dataframe extended cleaning labelling
def clean_txt_list(text):
    
    stopwords = nltk.corpus.stopwords.words('english')
    another = "idk,amp,aboard,about,above,gif,idk,absent,ive,weve,hes,shes,accordance,according,account,across,addition,after,against,ahead,along,alongside,also,although,amid,amidst,among,amongst,and,anent,anti,apart,around,as,aside,astride,at,athwart,atop,barring,because,before,behalf,behind,behither,below,beneath,beside,besides,between,betwixt,beyond,both,but,by,case,circa,close,concerning,considering,cum,despite,down,due,during,either,ere,even,except,excluding,failing,far,following,for,fornenst,fornent,from,front,given,if,in,including,inside,instead,into,lest,lieu,like,means,mid,minus,near,neither,next,nor,notwithstanding,of,off,on,once,only,onto,opposite,or,out,outside,outwith,over,owing,pace,past,per,place,plus,point,prior,pro,pursuant,qua,re,regard,regarding,regardless,regards,respect,round,sans,save,since,so,soon,spite,subsequent,than,thanks,that,though,through,throughout,till,times,to,top,toward,towards,under,underneath,unless,unlike,until,unto,up,upon,versus,via,vice,vis-à-vis,well,when,whenever,where,wherever,whether,while,with,within,without,worth,yet,a,able,about,across,after,all,almost,also,am,among,an,and,any,are,aren't,arent,as,at,be,because,been,but,by,can,cannot,could,dear,did,didn't,didnt,do,don't,dont,does,doesn't,doesnt,either,else,ever,every,for,from,get,got,had,has,have,he,her,hers,him,his,how,however,i,if,in,into,is,it,its,just,least,let,like,likely,may,me,might,most,must,my,neither,no,nor,not,of,off,often,on,only,or,other,our,own,rather,said,say,says,she,should,shouldn't,shouldnt,since,so,some,than,that,the,their,them,then,there,these,they,this,tis,to,too,twas,us,wants,was,wasn't,wasnt,we,were,weren't,werent,what,when,where,which,while,who,whom,why,will,with,would,yet,you,your,a's,able,about,above,according,accordingly,across,actually,after,afterwards,again,against,ain't,all,allow,allows,almost,alone,along,already,also,although,always,am,among,amongst,an,and,another,any,anybody,anyhow,anyone,anything,anyway,anyways,anywhere,apart,appear,appreciate,appropriate,are,aren't,around,as,aside,ask,asking,associated,at,available,away,awfully,be,became,because,become,becomes,becoming,been,before,beforehand,behind,being,believe,below,beside,besides,best,better,between,beyond,both,brief,but,by,c'mon,c's,came,can,can't,cannot,cant,cause,causes,certain,certainly,changes,clearly,co,com,come,comes,concerning,consequently,consider,considering,contain,containing,contains,corresponding,could,couldn't,course,currently,definitely,described,despite,did,didn't,didnt,different,do,does,doesnt,dontdoesn't,doing,don't,done,down,downwards,during,each,edu,eg,eight,either,else,elsewhere,enough,entirely,especially,et,etc,even,ever,every,everybody,everyone,everything,everywhere,ex,exactly,example,except,far,few,fifth,first,five,followed,following,follows,for,former,formerly,forth,four,from,further,furthermore,get,gets,getting,given,gives,go,goes,going,gone,got,gotten,greetings,had,hadn't,happens,hardly,has,hasn't,have,haven't,having,he,he's,hello,help,hence,her,here,here's,hereafter,hereby,herein,hereupon,hers,herself,hi,him,himself,his,hither,hopefully,how,howbeit,however,i'd,i'll,i'm,i've,ie,if,ignored,immediate,in,inasmuch,inc,indeed,indicate,indicated,indicates,inner,insofar,instead,into,inward,is,isnt,itd,itllitsisn't,it,it'd,it'll,it's,its,itself,just,keep,keeps,kept,know,knows,known,last,lately,later,latter,latterly,least,less,lest,let,let's,like,liked,likely,little,look,looking,looks,ltd,mainly,many,may,maybe,me,mean,meanwhile,merely,might,more,moreover,most,mostly,much,must,my,myself,name,namely,nd,near,nearly,need,needs,neither,never,nevertheless,new,next,nine,no,nobody,non,none,noone,nor,normally,not,nothing,novel,now,nowhere,obviously,of,off,often,oh,ok,okay,old,on,once,one,ones,only,onto,or,other,others,otherwise,ought,our,ours,ourselves,out,outside,over,overall,own,particular,particularly,per,perhaps,placed,please,plus,possible,presumably,probably,provides,que,quite,qv,rather,rd,re,really,reasonably,regarding,regardless,regards,relatively,respectively,right,said,same,saw,say,saying,says,secondly,see,seeing,seem,seemed,seeming,seems,seen,self,selves,sent,seriously,seven,several,shall,she,should,shouldn't,since,six,so,some,somebody,somehow,someone,something,sometime,sometimes,somewhat,somewhere,soon,sorry,specified,specify,specifying,still,sub,such,sup,sure,t's,take,taken,tell,tends,th,than,thank,thanks,thanx,that,that's,thats,the,their,theirs,them,themselves,then,thence,there,theres,there's,thereafter,thereby,therefore,therein,theres,thereupon,these,they,theyd,theyll,theyre,theyve,they'd,they'll,they're,they've,think,third,this,thorough,thoroughly,those,though,three,through,throughout,thru,thus,to,together,too,took,toward,towards,tried,tries,truly,try,trying,twice,two,un,under,unfortunately,unless,unlikely,until,unto,up,upon,us,use,used,useful,uses,using,usually,value,various,very,via,viz,vs,want,wants,was,wasnt,wed,well,wasn't,way,we,we'd,we'll,we're,we've,welcome,well,went,were,werent,whats,weren't,what,what's,whatever,when,whence,whenever,where,where's,whereafter,whereas,whereby,wherein,whereupon,wherever,whether,which,while,whither,who,who's,whoever,whole,whom,whose,why,will,willing,wish,with,within,without,won't,wonder,would,would,wouldn't,yes,yet,you,you'd,you'll,you're,you've,your,yours,yourself,yourselves,zero,reuters,ap,jan,feb,mar,apr,may,jun,jul,aug,sep,oct,nov,dec,tech,news,index,mon,tue,wed,thu,fri,sat,'s,a,a's,able,about,above,according,accordingly,across,actually,after,afterwards,again,against,ain't,all,allow,allows,almost,alone,along,already,also,although,always,am,amid,among,amongst,an,and,another,any,anybody,anyhow,anyone,anything,anyway,anyways,anywhere,apart,appear,appreciate,appropriate,are,aren't,around,as,aside,ask,asking,associated,at,available,away,awfully,b,be,became,because,become,becomes,becoming,been,before,beforehand,behind,being,believe,below,beside,besides,best,better,between,beyond,both,brief,but,by,c,c'mon,c's,came,can,can't,cannot,cant,cause,causes,certain,certainly,changes,clearly,co,com,come,comes,concerning,consequently,consider,considering,contain,containing,contains,corresponding,could,couldn't,course,currently,d,definitely,described,despite,did,didn't,different,do,does,doesn't,doing,don't,done,down,downwards,during,e,each,edu,eg,e.g.,eight,either,else,elsewhere,enough,entirely,especially,et,etc,etc.,even,ever,every,everybody,everyone,everything,everywhere,ex,exactly,example,except,f,far,few,fifth,five,followed,following,follows,for,former,formerly,forth,four,from,further,furthermore,g,get,gets,getting,given,gives,go,goes,going,gone,got,gotten,greetings,h,had,hadn't,happens,hardly,has,hasn't,have,haven't,having,he,he's,hello,help,hence,her,here,here's,hereafter,hereby,herein,hereupon,hers,herself,hi,him,himself,his,hither,hopefully,how,howbeit,however,i,i'd,i'll,i'm,i've,ie,i.e.,if,ignored,immediate,in,inasmuch,inc,indeed,indicate,indicated,indicates,inner,insofar,instead,into,inward,is,isn't,it,it'd,it'll,it's,its,itself,j,just,k,keep,keeps,kept,know,knows,known,l,lately,later,latter,latterly,least,less,lest,let,let's,like,liked,likely,little,look,looking,looks,ltd,m,mainly,many,may,maybe,me,mean,meanwhile,merely,might,more,moreover,most,mostly,mr.,ms.,much,must,my,myself,n,namely,nd,near,nearly,necessary,need,needs,neither,never,nevertheless,new,next,nine,no,nobody,non,none,noone,nor,normally,not,nothing,novel,now,nowhere,o,obviously,of,off,often,oh,ok,okay,old,on,once,one,ones,only,onto,or,other,others,otherwise,ought,our,ours,ourselves,out,outside,over,overall,own,p,particular,particularly,per,perhaps,placed,please,plus,possible,presumably,probably,provides,q,que,quite,qv,r,rather,rd,re,really,reasonably,regarding,regardless,regards,relatively,respectively,right,s,said,same,saw,say,saying,says,second,secondly,see,seeing,seem,seemed,seeming,seems,seen,self,selves,sensible,sent,serious,seriously,seven,several,shall,she,should,shouldn't,since,six,so,some,somebody,somehow,someone,something,sometime,sometimes,somewhat,somewhere,soon,sorry,specified,specify,specifying,still,sub,such,sup,sure,t,t's,take,taken,tell,tends,th,than,thank,thanks,thanx,that,that's,thats,the,their,theirs,them,themselves,then,thence,there,there's,thereafter,thereby,therefore,therein,theres,thereupon,these,they,they'd,they'll,they're,they've,think,third,this,thorough,thoroughly,those,though,three,through,throughout,thru,thus,to,together,too,took,toward,towards,tried,tries,truly,try,trying,twice,two,u,un,under,unfortunately,unless,unlikely,until,unto,up,upon,us,use,used,useful,uses,using,usually,uucp,v,value,various,very,via,viz,vs,w,want,wants,was,wasn't,way,we,we'd,we'll,we're,we've,welcome,well,went,were,weren't,what,what's,whatever,when,whence,whenever,where,where's,whereafter,whereas,whereby,wherein,whereupon,wherever,whether,which,while,whither,who,who's,whoever,whole,whom,whose,why,will,willing,wish,with,within,without,won't,wonder,would,would,wouldn't,x,y,yes,yet,you,you'd,you'll,you're,you've,your,yours,yourself,yourselves,z,zero,.com,.ly,.net,.org,aahh,aarrgghh,abt,ftl,ftw,fu,fuck,fucks,gtfo,gtg,haa,hah,hahah,haha,hahaha,hahahaha,hehe,heh,hehehe,hi,hihi,hihihi,http,https,huge,huh,huhu,huhuhu,idk,iirc,im,imho,imo,ini,irl,ish,isn,isnt,j/k,jk,jus,just,justwit,juz,kinda,kthx,kthxbai,kyou,laa,laaa,lah,lanuch,leavg,leh,lol,lols,ltd,mph,mrt,msg,msgs,muahahahahaha,nb,neways,ni,nice,pls,plz,plzz,psd,pte,pwm,pwned,qfmft,qft,tis,tm,tmr,tyty,tyvm,um,umm,viv,vn,vote,voted,w00t,wa,wadever,wah,wasn,wasnt,wassup,wat,watcha,wateva,watever,watnot,wats,wayy,wb,weren,werent,whaha,wham,whammy,whaow,whatcha,whatev,whateva,whatevar,whatever,whatnot,whats,whatsoever,whatz,whee,whenz,whey,whore,whores,whoring,win,wo,woah,woh,wooohooo,woot,wow,wrt,wtb,wtf,wth,wts,wtt,www,xs,ya,yaah,yah,yahh,yahoocurrency,yall,yar,yay,yea,yeah,yeahh,yeh,yhoo,ymmv,young,youre,yr,yum,yummy,yumyum,yw,zomg,zz,zzz,loz,lor,loh,tsk,meh,lmao,wanna,doesn,liao,didn,didnt,omg,ohh,ohgod,hoh,hoo,bye,byee,byeee,byeeee,lmaolmao,yeah,yeahh,yeahhh,yeahhhh,yeahhhhh,yup,yupp,hahahahahahaha,hahahahahah,hahhaha,wooohoooo,wahaha,haah,2moro,veh,noo,nooo,noooo,hahas,ooooo,ahahaha,ahahahahah,tomolow,.com,.ly,.net,.org,aahh,aarrgghh,abt,accent,accented,accents,acne,ads,afaik,aft,ago,ahead,ain,aint,aircon,alot,am,annoy,annoyed,annoys,anycase,anymore,app,apparently,apps,argh,ass,asses,awesome,babeh,bad,bai,based,bcos,bcoz,bday,bit,biz,blah,bleh,bless,blessed,blk,blogcatalog,bro,bros,btw,byee,com,congrats,contd,conv,cos,cost,costs,couldn,couldnt,cove,coves,coz,crap,cum,curnews,curr,cuz,dat,de,didn,didnt,diff,dis,doc,doesn,doesnt,don,dont,dr,dreamt,drs,due,dun,dunno,duper,eh,ehh,emo,emos,eng,esp,fadein,ffs,fml,frm,ftl,ftw,fu,fuck,fucks,fwah,g2g,gajshost,gd,geez,gg,gigs,gtfo,gtg,haa,haha,hahaha,hasn,hasnt,hav,haven,havent,hee,heh,hehe,hehehe,hello,hey,hi,hmm,ho,hohoho,http,https,huh,huhu,huhuhu,idk,iirc,im,imho,imo,info,ini,irl,ish,isn,isnt,issued,j/k,jk,jus,just,justwit,juz,kinda,kthx,kthxbai,kyou,laa,laaa,lah,lanuch,lawl,leavg,leh,lfg,lfm,ll,lmao,lmfao,lnks,lol,lols,lotsa,lotta,ltd,luv,ly,macdailynews,meh,mph,msg,msgs,muahahahahaha,nb,neato,ni,nite,nom,noscript,nvr,nw,ohayo,omfg,omfgwtf,omg,omgwtfbbq,omw,org,pf,pic,pls,plz,plzz,pm,pmsing,ppl,pre,pro,psd,pte,pwm,pwned,qfmft,qft,rawr,rawrr,rofl,roflmao,rss,rt,sec,secs,seem,seemed,seems,sgreinfo,shd,shit,shits,shitz,shld,shouldn,shouldnt,shudder,sq,sqft,sqm,srsly,stfu,stks,su,suck,sucked,sucks,suckz,sux,swf,tart,tat,tgif,thanky,thk,thks,tht,tired,tis,tm,tmr,tsk,ttyl,ty,tym,tyme,typed,tyty,tyvm,um,umm,va,valid,valids,var,vc,ve,viv,vn,w00t,wa,wadever,wah,wasn,wasnt,wassup,wat,watcha,wateva,watnot,wats,wayy,wb,web,website,websites,weren,werent,whaha,wham,whammy,whaow,whatcha,whatev,whateva,whatevar,whatever,whatnot,whats,whatsoever,whatz,whee,whenz,whey,whore,whores,whoring,wo,woah,woh,wooohooo,woot,wow,wrt,wtb,wtf,wth,wts,wtt,www,xs,ya,yaah,yah,yahh,yahoocurrency,yall,yar,yay,yea,yeah,yeahh,year,yearly,years,yeh,yhoo,ymmv,young,youre,yr,yum,yummy,yumyum,yw,zomg,zz,zzz,fucking,mrs,mr,eh,ehh,ehhh,lot,lots,http,html,com,ly,net,org,hahahahahahahahaha,hahahahaha,hahahahah,zzzzz,#teamfollowback,#teamfollow,#follow,#autofollow,#followgain,#followbackk,#teamautofollow,#followme,#ifollow,#followngain,#followback,#followfriday,#ifollowback,#200aday,#500aday,#1000aday,hahahahha,lolololol,lololol,lolol,lol,dude,hmmm,humm,tumblr,kkkk,fk,yayyyyyy,fffffffuuuuuuuuuuuu,zzzz,zzzzz,noooooooooo,noo,nooo,noooo,hahahhaha,woohoo,lalalalalalala,lala,lalala,lalalala,whahahaahahahahahah,.com,.ly,.net,.org,aahh,aarrgghh,abt,ftl,ftw,fu,fuck,fucks,gtfo,gtg,haa,hah,hahah,haha,hahaha,hahahaha,hehe,heh,hehehe,hi,hihi,hihihi,http,https,huge,huh,huhu,huhuhu,idk,iirc,im,imho,imo,ini,irl,ish,isn,isnt,j/k,jk,jus,just,justwit,juz,kinda,kthx,kthxbai,kyou,laa,laaa,lah,lanuch,leavg,leh,lol,lols,ltd,mph,mrt,msg,msgs,muahahahahaha,nb,neways,ni,nice,pls,plz,plzz,psd,pte,pwm,pwned,qfmft,qft,tis,tm,tmr,tyty,tyvm,um,umm,viv,vn,vote,voted,w00t,wa,wadever,wah,wasn,wasnt,wassup,wat,watcha,wateva,watever,watnot,wats,wayy,wb,weren,werent,whaha,wham,whammy,whaow,whatcha,whatev,whateva,whatevar,whatever,whatnot,whats,whatsoever,whatz,whee,whenz,whey,whore,whores,whoring,win,wo,woah,woh,wooohooo,woot,wow,wrt,wtb,wtf,wth,wts,wtt,www,xs,ya,yaah,yah,yahh,yahoocurrency,yall,yar,yay,yea,yeah,yeahh,yeh,yhoo,ymmv,young,youre,yr,yum,yummy,yumyum,yw,zomg,zz,zzz,loz,lor,loh,tsk,meh,lmao,wanna,doesn,liao,didn,didnt,omg,ohh,ohgod,hoh,hoo,bye,byee,byeee,byeeee,lmaolmao,yeah,yeahh,yeahhh,yeahhhh,yeahhhhh,yup,yupp,hahahahahahaha,hahahahahah,hahhaha,wooohoooo,wahaha,haah,2moro,veh,noo,nooo,noooo,hahas,ooooo,ahahaha,ahahahahah,tomolow,.com,.ly,.net,.org,aahh,aarrgghh,abt,accent,accented,accents,acne,ads,afaik,aft,ago,ahead,ain,aint,aircon,alot,am,annoy,annoyed,annoys,anycase,anymore,app,apparently,apps,argh,ass,asses,awesome,babeh,bad,bai,based,bcos,bcoz,bday,big,bigger,biggest,bit,biz,blah,bleh,bless,blessed,blk,blogcatalog,bored,boring,bright,bring,brings,bro,broke,broken,bros,brought,btw,bye,byebye,byee,cheap,clutter,cluttered,com,common,complete,completed,completes,completing,congrats,congratulation,congratulations,consecutive,consecutively,contd,continue,continues,conv,cos,cost,costs,couldn,couldnt,cove,coves,coz,crap,crappy,crazy,crowded,cum,curnews,curr,cute,cuties,cuz,daily,damn,dark,dat,days,de,dear,didn,didnt,diff,dis,distracted,distracts,doc,doesn,doesnt,don,dont,door,doors,double,doubled,doubles,dr,dreamt,drs,due,dun,dunno,duper,earlier,earliest,early,earn,earned,earns,easier,easy,eat,eaten,eats,eh,ehh,emo,emos,enable,enables,enabling,eng,enter,entered,enters,esp,everyday,everywhere,exclude,excluded,excludes,excuse,excused,excuses,explode,exploded,explodes,eye,eyes,fadein,fail,failed,fails,fake,fall,falls,false,famous,fast,faster,fastest,fat,featured,feel,feeling,feels,fell,felt,ffs,finally,find,finds,finish,finished,flat,flats,flight,flights,fml,follow,followed,follows,food,form,formed,forming,forms,found,free,fries,frm,ftl,ftw,fu,fuck,fucks,full,fully,fun,funny,furnish,furnished,future,fwah,g2g,gajshost,gave,gd,geez,gg,gigs,gimme,give,giveaway,giveaways,given,gives,gonna,good,goodbye,goodnight,got,gotta,grats,gratz,great,greats,gtfo,gtg,guess,guessing,haa,haha,hahaha,happen,happened,happens,hard,harder,hardest,hasn,hasnt,hate,hated,hates,hav,haven,havent,hdb,hear,heard,hears,heart,hee,heh,hehe,hehehe,hello,hey,hi,highest,hmm,ho,hohoho,hopefully,hoping,host,hosted,hosts,hot,hour,hours,http,https,huge,huh,huhu,huhuhu,hurt,hurts,idiot,idiots,idk,iirc,im,imho,imo,important,indicate,indicated,indicates,indicating,info,ini,install,interact,interacted,interacting,interacts,interested,interesting,involve,involved,involves,irl,ish,isn,isnt,issued,j/k,jk,jus,just,justwit,juz,kill,killed,kills,kinda,kthx,kthxbai,kyou,laa,laaa,lah,lanuch,last,late,later,latest,laugh,laughed,laughs,launched,launches,lawl,learn,learned,learns,leavg,leh,lend,lender,lenders,lfg,lfm,lightly,like,liked,likes,lined,listed,listen,listened,listening,listens,live,lived,ll,lmao,lmfao,lnks,loaned,local,locate,located,locates,lock,locked,locks,lol,lols,look,looked,looking,looks,lose,loss,lot,lotsa,lotta,love,loved,loves,lowest,ltd,luv,ly,macdailynews,mad,made,mailed,main,make,makes,manage,managed,manages,march,may,mean,means,mee,meet,meets,meh,mention,mentioned,mentions,met,million,millions,min,mine,mini,mins,miss,missed,misses,mix,mixed,mixes,monthly,mph,mrt,msg,msgs,muahahahahaha,mum,named,national,nb,neato,negotiable,net,neways,newly,news,ni,nice,night,nite,nom,noscript,notice,notices,noticing,notified,notifies,notify,now,nowadays,nvr,nw,obvious,obviously,occur,occured,occurs,october,office,offices,ohayo,old,omfg,omfgwtf,omg,omgwtfbbq,omw,online,only,open,opened,opens,opportunities,opportunity,order,ordered,ordering,orders,org,organize,organized,organizes,pack,packed,packs,paid,pain,painful,painless,pains,pair,park,parks,passed,past,pay,pays,pf,phew,phone,phones,pic,pick,picked,picks,pics,pictures,pig,pigs,pissed,place,places,play,played,plays,pls,plz,plzz,pm,pmsing,post,posted,posts,powerful,ppl,pre,prefer,present,presented,presents,pretty,preview,previewed,previews,previous,priced,primary,private,pro,produce,produced,produces,prolly,prosperous,provide,provided,provides,psd,pte,purchase,purchased,purchases,pwm,pwned,qfmft,qft,quality,quick,ran,rate,rated,rawr,rawrr,reader,readers,real,realise,realised,realises,realize,realized,realizes,receive,received,receives,recent,recently,recommend,recommended,recommends,recover,recovered,recovers,refuse,refused,refuses,regular,rejoice,relate,related,relates,remember,remembered,remembers,remind,reminded,reminds,remove,removed,removes,rename,renamed,renames,rent,rental,rented,rents,replace,replaced,replaces,replied,replies,reply,reported,reports,requested,require,required,requires,resort,resorts,resulted,return,returned,returns,review,reviewed,reviews,right,rightaway,rofl,roflmao,rss,rt,run,runs,safe,safety,sale,sales,sang,save,saved,saves,scratch,scratched,scratches,screwed,screws,search,searched,searches,sec,secondary,secs,seem,seemed,seems,select,selected,selecting,selects,sell,sells,send,sends,sent,serve,served,serves,set,sets,settle,settled,settles,sg,sgd,sgreinfo,share,shared,shares,shd,shit,shits,shitz,shld,shortest,shouldn,shouldnt,show,showed,shown,shows,shudder,sick,sicks,side,sides,signed,significant,significantly,similar,similars,sing,singaporestd,single,singled,singles,sings,site,sites,skin,sleep,sleeps,slept,slight,slightly,slipped,slow,small,sms,soba,soft,sold,somemore,soon,sore,sores,sound,sounded,sounds,soup,soups,source,sources,special,specials,specific,specifically,spend,spending,spends,spent,spot,spots,sq,sqft,sqm,srsly,start,started,starts,stay,stayed,stays,stfu,stks,stop,stopped,stops,stories,story,strong,student,students,studied,studies,study,stuff,stupid,stupids,su,suck,sucked,sucks,suckz,sue,sued,sues,sunday,sundays,sung,support,supported,supporting,supports,sux,sweet,swf,sync,take,takes,taking,talk,talked,talks,tallest,target,targets,tart,tat,taught,tbh,tbl,teach,teaches,teehee,tel,tells,tgif,thank,thanks,thanky,theme,themes,thing,things,think,thinks,thk,thks,tht,tired,tis,tm,tmr,today,toilet,toilets,told,tomorrow,tonight,took,total,totals,treat,treated,treats,tree,trees,true,tsk,ttyl,turned,turns,twittering,ty,tym,tyme,typed,tyty,tyvm,um,umm,unit,units,update,updated,updates,upgrade,upgraded,upgrades,upload,uploaded,uploads,va,valid,valids,var,vc,ve,visit,visited,visits,viv,vn,w00t,wa,wadever,wah,wait,waited,waiting,waits,wanna,want,wanted,wants,wasn,wasnt,wassup,wat,watch,watcha,watched,watches,watching,wateva,watever,watnot,wats,wayy,wb,web,website,websites,wednesday,week,weekly,weeks,weird,weren,werent,whaha,wham,whammy,whaow,whatcha,whatev,whateva,whatevar,whatever,whatnot,whats,whatsoever,whatz,whee,whenz,whey,white,whore,whores,whoring,win,wins,wish,wished,wishes,wo,woah,woh,woman,women,womens,won,wonder,wondered,wondering,wonders,wooohooo,woot,word,words,work,working,works,world,worlds,worse,worst,wow,write,writes,written,wrong,wrote,wrt,wtb,wtf,wth,wts,wtt,www,xs,ya,yaah,yah,yahh,yahoocurrency,yall,yar,yay,yea,yeah,yeahh,year,yearly,years,yeh,yhoo,ymmv,young,youre,yr,yum,yummy,yumyum,yw,zomg,zz,zzz,girl,girls,boy,boys,man,men,mens,mans,guy,guys,fucking,mrs,mr,miss,eh,ehh,ehhh,lot,lots,http,html,com,ly,net,org,hahahahahahahahaha,hahahahaha,first,second,third,1st,2nd,3rd,hahahahah,zzzzz,#teamfollowback,#teamfollow,#follow,#autofollow,#followgain,#followbackk,#teamautofollow,#followme,#ifollow,#followngain,#followback,#followfriday,#ifollowback,tweet,tweets,#200aday,#500aday,#1000aday,thing,things,think,thinks,thinking,hahahahha,lolololol,lololol,lolol,lol,dude,hmmm,humm,tumblr,morning,noon,afternoon,today,evening,birthday,birthdays,kkkk,fk,yayyyyyy,fffffffuuuuuuuuuuuu,zzzz,zzzzz,noooooooooo,noo,nooo,noooo,hahahhaha,#ff,#followback,#teamfollowback,#f4f,#autofollow,#500aday,#instantfollowback,#autofollowback,#1000aday,#ifollowback,#teamautofollow,#f4f,#instantfollow,#autofollow,.com,.ly,.net,.org,aahh,aarrgghh,abt,accent,accented,accents,account,accounts,acne,activities,activity,ad,add,added,adding,adds,admission,admissions,ads,afaik,affiliate,affiliates,affirmation,affirmations,aft,afternoon,ago,ahead,ain,aint,aircon,album,albums,allergies,allergy,allow,allowed,allows,alot,am,angry,announcement,announcements,annoy,annoyed,annoys,anycase,anymore,app,apparently,approve,approved,approves,apps,april,area,areas,argh,arrive,arrived,arrives,article,articles,asia,asian,ask,asked,asks,ass,asses,ate,attempt,attempting,attempts,attend,attended,attends,august,auto,autoindustry,awesome,babeh,babies,baby,back,backed,bad,bag,bags,bai,balance,bank,banks,based,bcos,bcoz,bday,bed,bedroom,belong,belonged,belongs,big,bigger,biggest,billion,billons,birthday,birthdays,bit,biz,blah,bleh,bless,blessed,blk,blog,blogcatalog,blogger,bloggers,blogging,blogs,bloody,book,bored,boring,bottle,bottles,bought,box,boxes,boy,boys,break,breakfast,breakfasts,bright,bring,brings,bro,broke,broken,bros,brought,btw,build,builds,built,bus,buses,butter,buy,buys,bye,byebye,byee,call,called,calls,cancel,canceled,cancelled,cancels,candies,candy,car,career,careers,cars,catch,catches,caught,change,changed,changes,changing,channel,channels,cheap,check,checked,checks,chicken,chickens,chocolate,chocolates,choice,choices,class,classes,click,close,closed,closes,cloth,clothe,clothes,clutter,cluttered,cna,coffee,com,comeback,comment,commenting,comments,common,companies,company,complete,completed,completes,completing,conditions,condo,condominium,condominoums,condos,congrats,congratulation,congratulations,consecutive,consecutively,consult,consultant,consults,contact,contacted,contacts,contd,content,contents,continue,continues,conv,cookies,cos,cost,costs,couldn,couldnt,countries,country,couple,couples,course,courses,cove,coves,coz,crap,crappy,crazy,cream,create,created,creates,creats,crowded,cum,curnews,curr,customer,customers,cute,cuties,cuz,dad,daily,damn,dark,dat,date,dated,dates,day,days,de,dead,dear,death,december,depend,depended,depends,deposit,deposited,deposits,detail,details,didn,didnt,die,died,dies,diff,dinner,dinners,dis,distract,distracted,distracts,doc,docs,document,documents,doesn,doesnt,don,dont,door,doors,double,doubled,doubles,download,downloads,dr,dreamt,drs,due,dun,dunno,duper,earlier,earliest,early,earn,earned,earns,easier,easy,eat,eaten,eats,eh,ehh,email,emails,emo,emos,enable,enables,enabling,end,ends,eng,enter,entered,enters,esp,event,events,everyday,everywhere,exclude,excluded,excludes,excuse,excused,excuses,explode,exploded,explodes,eye,eyes,fadein,fail,failed,fails,fake,fall,falls,false,families,family,famous,fast,faster,fastest,fat,favorite,favorited,favorites,favourite,favourites,featured,february,feed,feeds,feel,feeling,feels,fell,felt,female,females,ffs,finally,find,finds,finish,finished,flat,flats,flight,flights,fml,follow,followed,follows,food,form,formed,forming,forms,found,free,friday,friend,friends,fries,frm,fruit,fruits,ftl,ftw,fu,fuck,fucks,full,fully,fun,funny,furnish,furnished,future,fwah,g2g,gajshost,gave,gd,geez,gg,gift,gifted,gifts,gigs,gimme,girl,girls,give,giveaway,giveaways,given,gives,gonna,good,goodbye,goodnight,got,gotta,grats,gratz,great,greats,gtfo,gtg,guess,guessing,guy,guys,haa,haha,hahaha,hair,hairs,hand,hands,happen,happened,happens,hard,harder,hardest,hasn,hasnt,hate,hated,hates,hav,haven,havent,hdb,hear,heard,hears,heart,hee,heh,hehe,hehehe,hello,hey,hi,highest,hmm,ho,hohoho,holiday,holidays,home,homework,homeworks,hope,hopefully,hoping,host,hosted,hosts,hot,hour,hours,http,https,huge,huh,huhu,huhuhu,hurt,hurts,idea,ideas,idiot,idiots,idk,iirc,im,imho,imo,important,indicate,indicated,indicates,indicating,info,information,ini,install,installation,installations,installs,interact,interacted,interacting,interaction,interactions,interacts,interested,interesting,internet,introduction,introductions,involve,involved,involves,irl,ish,isn,isnt,issue,issued,issues,item,items,j/k,january,jk,job,jobs,july,june,jus,just,justwit,juz,key,keys,kid,kids,kill,killed,kills,kinda,kthx,kthxbai,kyou,laa,laaa,lah,lanuch,last,late,later,latest,laugh,laughed,laughs,launched,launches,lawl,learn,learned,learns,leavg,leh,lend,lender,lenders,lfg,lfm,life,light,lightly,lights,like,liked,likes,line,lined,lines,link,links,listed,listen,listened,listening,listens,live,lived,lives,ll,lmao,lmfao,lnks,loaned,local,locate,located,locates,location,locations,lock,locked,locks,lol,lols,look,looked,looking,looks,lose,loss,lot,lotsa,lotta,love,loved,loves,lowest,ltd,lunch,lunches,luv,ly,macdailynews,mad,made,mailed,main,make,makes,male,males,man,manage,managed,manages,march,may,mean,means,media,medias,mee,meet,meets,meh,men,mens,mention,mentioned,mentions,menu,menus,merry,message,messages,met,million,millions,min,mine,mini,mins,minute,minutes,miss,missed,misses,mix,mixed,mixes,mom,monday,money,month,monthly,months,morning,movie,movies,mph,mrt,msg,msgs,muahahahahaha,mum,mushroom,music,musics,named,national,nb,neato,negotiable,net,neways,newly,news,ni,nice,night,nite,nom,noodle,noodles,noscript,notes,notice,notices,noticing,notified,notifies,notify,november,now,nowadays,nvr,nw,obvious,obviously,occur,occured,occurs,october,office,offices,ohayo,old,omfg,omfgwtf,omg,omgwtfbbq,omw,online,only,open,opened,opens,opportunities,opportunity,order,ordered,ordering,orders,org,organize,organized,organizes,pack,packed,packs,page,pages,paid,pain,painful,painless,pains,pair,parent,parents,park,parks,passed,past,pay,pays,people,person,pf,phew,phone,phones,photo,photos,pic,pick,picked,picks,pics,pictures,pig,pigs,pissed,place,places,play,played,plays,pls,plz,plzz,pm,pmsing,post,posted,posts,powerful,ppl,pre,prefer,present,presentation,presentations,presented,presents,pretty,preview,previewed,previews,previous,price,priced,prices,primary,private,pro,problem,problems,produce,produced,produces,product,production,productions,products,profile,profiles,programs,project,projects,prolly,prosperous,provide,provided,provides,psd,pte,public,purchase,purchased,purchases,pwm,pwned,qfmft,qft,quality,quick,ran,rate,rated,rawr,rawrr,reader,readers,real,realise,realised,realises,realize,realized,realizes,receive,received,receives,recent,recently,recommend,recommended,recommends,recover,recovered,recovers,refuse,refused,refuses,regular,rejoice,relate,related,relates,remember,remembered,remembers,remind,reminded,reminds,remove,removed,removes,rename,renamed,renames,rent,rental,rented,rents,replace,replaced,replaces,replied,replies,reply,report,reported,reports,request,requested,requests,require,required,requires,resort,resorts,result,resulted,results,return,returned,returns,retweet,retweets,review,reviewed,reviews,rice,right,rightaway,road,roads,rocks,rofl,roflmao,role,roles,room,rooms,rss,rt,run,runs,safe,safety,sale,sales,sang,saturday,save,saved,saves,scratch,scratched,scratches,screen,screened,screens,screwed,screws,search,searched,searches,season,seasons,sec,secondary,secs,seem,seemed,seems,select,selected,selecting,selects,sell,sells,send,sends,sent,september,serve,served,serves,service,services,set,sets,settle,settled,settles,sg,sgd,sgreinfo,share,shared,shares,shd,shit,shits,shitz,shld,shoe,shoes,shop,shops,shortest,shouldn,shouldnt,show,showed,shown,shows,shudder,sick,sicks,side,sides,signed,significant,significantly,similar,similars,sing,singapore,singaporestd,single,singled,singles,sings,site,sites,skin,sleep,sleeps,slept,slight,slightly,slipped,slow,small,sms,soba,soft,sold,somemore,son,sons,soon,sore,sores,sound,sounded,sounds,soup,soups,source,sources,special,specials,specific,specifically,spend,spending,spends,spent,spot,spots,sq,sqft,sqm,srsly,start,started,starts,stay,stayed,stays,stfu,stks,stop,stopped,stops,stories,story,strong,student,students,studied,studies,study,stuff,stupid,stupids,su,suck,sucked,sucks,suckz,sue,sued,sues,sunday,sundays,sung,support,supported,supporting,supports,sux,sweet,swf,sync,take,takes,taking,talk,talked,talks,tallest,target,targets,tart,tat,taught,tbh,tbl,tea,teach,teacher,teachers,teaches,teehee,tel,tells,tgif,thank,thanks,thanky,theme,themes,thing,things,think,thinks,thk,thks,thought,throat,throats,tht,thursday,ticket,tickets,time,tips,tired,tis,tm,tmr,today,toilet,toilets,told,tomorrow,tonight,took,total,totals,treat,treated,treats,tree,trees,true,tsk,ttyl,tuesday,turn,turned,turns,tweet,tweeting,tweets,twittering,ty,tym,tyme,type,typed,types,tyty,tyvm,um,umm,unit,units,update,updated,updates,upgrade,upgraded,upgrades,upload,uploaded,uploads,url,urls,usb,usd,user,users,va,valid,valids,var,vc,ve,version,versions,video,videos,visit,visited,visits,viv,vn,vote,voted,votes,w00t,wa,wadever,wah,wait,waited,waiting,waits,wanna,want,wanted,wants,wasn,wasnt,wassup,wat,watch,watcha,watched,watches,watching,wateva,watever,watnot,wats,wayy,wb,web,website,websites,wednesday,week,weekly,weeks,weird,weren,werent,whaha,wham,whammy,whaow,whatcha,whatev,whateva,whatevar,whatever,whatnot,whats,whatsoever,whatz,whee,whenz,whey,white,whore,whores,whoring,win,wins,wish,wished,wishes,wo,woah,woh,woman,women,womens,won,wonder,wondered,wondering,wonders,wooohooo,woot,word,words,work,working,works,world,worlds,worse,worst,wow,write,writes,written,wrong,wrote,wrt,wtb,wtf,wth,wts,wtt,www,xs,ya,yaah,yah,yahh,yahoocurrency,yall,yar,yay,yea,yeah,yeahh,year,yearly,years,yeh,yesterday,yhoo,ymmv,young,youre,yr,yum,yummy,yumyum,yw,zomg,zz,zzz"
    additional = another.split(",")
    stopwords += additional 
   
    text = re.sub(r'@[A-Za-z0-9]+', '', text) #removed @mentions
    text = re.sub(r'#', '', text) #removing the # symbols
    text = re.sub(r'RT[\s]+', '',  text) # removing RT
    text = ''.join([i for i in text if not i.isdigit()]) #removing digits
    text = re.sub(r'https?:\/\/\S+', '', text) #Remove the hyper link
    text = text.lower() # lowercase
    text =  ' '.join(word.strip(string.punctuation) for word in text.split()) #remove punctuations
    tokens = re.split('\W+', text)
    text = [word for word in tokens if word not in stopwords] #remove stopwords   
    
    return text

# Twitter table dataframe creation
def tweet_search(query, resulttype):
    
    tweets_search = tweepy.Cursor(api.search, q = query+ ' -filter:retweets', lang = 'en' , result_type = resulttype, tweet_mode='extended').items(15)
    tweets_list = []
    url_list = []
    date_list = []


    for tweet in tweets_search:
        tweets_list.append(tweet.full_text) 
        date = tweet.created_at.strftime("%Y/%m/%d")
        date_list.append(date)        
        url = f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"
        url_list.append(url)     

    data = {'Tweets': tweets_list, 'url': url_list, 'date': date_list}
    df = pd.DataFrame(data) 
    
    df['Tweets'] = df['Tweets'].apply(clean_txt)  
    df['CleanedList'] = df['Tweets'].apply(clean_txt_list)

    senti_score = []    
    result = []
   
    for index, row in df.iterrows():
        analyzer = SentimentIntensityAnalyzer()
        vs = analyzer.polarity_scores(row['Tweets'])  
        compound = vs.get('compound')         
       
       
        
        if compound >= 0.05:
            result.append('Positive')
        elif compound <= -0.05:
            result.append('Negative')
        else:
            result.append('Neutral')    

  
    df['Sentiment'] = result   

    return df

# Twitter bargraph dataframe creation
def twt_top_mentioned(df,query):
    word_list = []
    for index, rows in df.iterrows():
        for each_word in rows.CleanedList:
            if each_word not in word_list:
                if len(each_word) > 3 and each_word != query:
                    word_list.append(  " " +each_word + " ")      
    
        
    counts = dict()
    for word in word_list:
        if word in counts:
            counts[word] += 1
        else:
            counts[word] = 1
            

    df = pd.DataFrame(list(counts.items()),columns = ['word','count'])     
    df = df.sort_values(['count'], ascending=[False])
    
    return df

# Twitter piechart dataframe creation
def overallsentiment(df):
    
    #get the percentage of positive tweets
    postweets = df[df.Sentiment == 'Positive']
    postweets = postweets['Tweets']
    
    # get the percentage of negative tweets
    negtweets = df[df.Sentiment == 'Negative']
    negtweets = negtweets['Tweets']
    
    #get the percentage of neutral tweets
    neutweets = df[df.Sentiment == 'Neutral']
    neutweets = neutweets['Tweets']
    
    tweets = {'Sentiment': ['Positive','Negative','Neutral'],
        'Overall Score': [round((postweets.shape[0] / df.shape[0]) *100, 1),round( (negtweets.shape[0] / df.shape[0] * 100) , 1), round( (neutweets.shape[0] / df.shape[0] * 100) , 1)]
        }
    df = pd.DataFrame(tweets, columns = ['Sentiment', 'Overall Score'])
    
    return df

# Twitter timeseries dataframe creation
def time_series(query):  

    tweets_search = tweepy.Cursor(api.search, q = query+ ' -filter:retweets', result_type = 'recent', lang = 'en' , tweet_mode='extended').items(100)    

    tweets_list = []
    date_time = []

    for tweet in tweets_search:
        tweets_list.append(tweet.full_text) 
        tweet.created_at += timedelta(hours=8)
        date_time.append(tweet.created_at)

    data = {'Tweets': tweets_list,  'Date_Time': date_time}
    df = pd.DataFrame(data) 
          
    df['Cleaned'] = df['Tweets'].apply(clean_txt)

    senti_score = []    
    for index, row in df.iterrows():
        analyzer = SentimentIntensityAnalyzer()
        vs = analyzer.polarity_scores(row['Cleaned'])  
        compound = vs.get('compound')         
        senti_score.append(round(compound,2))          
  
    df['Sentiment'] = senti_score   

    df_sampled = df.set_index('Date_Time').resample('20S').mean().reset_index()
    df_sampled['Sentiment'] = df_sampled['Sentiment'].fillna(0)
    df_sampled['Date_Time'] = df_sampled['Date_Time'].dt.time
    
    return df_sampled

# Using Sentiment to implement color on table rows
def quick_color(s):

    if s == "Positive":
        return "green"

    elif s == "Negative":
        return "crimson"

    else:
        return "#EAECEE"

# News table headers
news_table_header = html.Table(
    className="unresponsive-table-header",
    children=[
        html.Thead(
            html.Tr(
                children=[
                    html.Th("News title",style={'font-family': 'verdana','font-size':11,'text-align': 'left','width':'65.5%','border': '1px solid lightgrey','color':'#003B70'}),
                    html.Th("Date",style={'font-family': 'verdana','font-size':11,'text-align': 'center','width':'16.5%','border': '1px solid lightgrey','color':'#003B70'}),
                    html.Th("Sentiment",style={'font-family': 'verdana','font-size':11,'text-align': 'center','width':'17%','border': '1px solid lightgrey','color':'#003B70'}),
                ],
                style={'color':'#000000','background': '#f8f8ff'}
                )
            ),
        ],
    style={
        'border': '1px solid lightgrey', 
        'vertical-align': 'bottom',
        'width':'100%'
        },
)

# Twitter table headers
twitter_table_header = html.Table(
    className="unresponsive-table-header",
    children=[
        html.Thead(
            html.Tr(
                children=[
                    html.Th("Tweet",style={'font-family': 'verdana','font-size': 11,'text-align': 'left','width':'65.5%','border': '1px solid lightgrey','color':'#003B70'}),
                    html.Th("Date",style={'font-family': 'verdana','font-size': 11,'text-align': 'center','width':'16.5%','border': '1px solid lightgrey','color':'#003B70'}),
                    html.Th("Sentiment",style={'font-family': 'verdana','font-size': 11,'text-align': 'center','width':'17%','border': '1px solid lightgrey','color':'#003B70'}),
                ],
                style={'color':'#000000','background': '#f8f8ff'}
                )
            ),
        ],
    style={
        'border': '1px lightgrey', 
        'vertical-align': 'bottom',
        'width':'100%'
        },
)

# Tab selection styling
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#003B70',
    'color': 'white',
    'padding': '6px'
}

# Bloomberg image replacement
def check_if_bloomberg(url,source):
    if source == "bloomberg" or source == None:
        return "https://cdn.i-scmp.com/sites/default/files/styles/320x320/public/d8/images/author/pic/2020/07/09/bloomberg_news.jpg?itok=VJXDxQfn"
    return url
    
# News table
def generate_news_table(news_df,source):
    return html.Table(
        className="responsive-table",
        children=html.Tbody([
            html.Tr(
                children=[
                    html.Td(html.Img(src=check_if_bloomberg(d[2],source),width=90,height=52,style={'border':'1px solid lightgrey'}),style={'width':'15%'}),
                    html.Td(html.A(href=d[1],children=d[0],style={'font-family': 'verdana','height':15,'color':'#000000','font-size': 11}),style={'width':'53%','border': '1px solid lightgrey','padding-left':10,'padding-right':10,'line-height':12}),
                    html.Td(d[4],style={'font-family': 'verdana','height':15,'text-align': 'center','width':'17%','border': '1px solid lightgrey','font-size': 11}),
                    html.Td(d[3],style={'font-family': 'verdana','height':15,'text-align': 'center','width':'15%','border': '1px solid lightgrey','font-size': 11}),
                ], 
                style={'height':35,'color':'#000000','background-color':quick_color(d[3])})
                for d in news_df.values.tolist()]),
        style={
            'border': '1px solid lightgrey', 
            'text-align': 'left',
            'vertical-align': 'bottom',
            'width':'100%',
            'height': 470, 'overflow-y':'scroll','display':'block'
            },
    )

# Twitter Popular & Recent tables
def generate_twitter_table(twitter_df):
    return html.Table(
        className="responsive-table",
        children=html.Tbody([
            html.Tr(
                children=[
                    html.Td(html.A(href=d[2],children=d[0],style={'font-family': 'verdana','height':20,'color':'#000000','font-size': 11}),style={'width':'68%','border': '1px solid lightgrey','padding':10,'line-height':12}),
                    html.Td(d[3],style={'font-family': 'verdana','text-align': 'center','height':20,'width':'17%','border': '1px solid lightgrey','font-size': 11}),
                    html.Td(d[1],style={'font-family': 'verdana','text-align': 'center','height':20,'width':'15%','border': '1px solid lightgrey','font-size': 11}),
                ], 
                style={'height':35,'color':'#000000','background-color':quick_color(d[1])})
                for d in twitter_df.values.tolist()]),
        style={
            'border': '1px solid lightgrey', 
            'text-align': 'left',
            'vertical-align': 'bottom',
            'width':'100%',
            'height':215, 'overflow-y':'scroll','display':'block'
            },
    )

# News & Twitter piechart
def generate_piechart(breakdown_df):
    return dcc.Graph(
        figure = px.pie(
            breakdown_df, values='Overall Score', 
            names='Sentiment', width=290, height=170, color="Sentiment",
            # color_discrete_sequence=px.colors.qualitative.Pastel, 
            color_discrete_map={'Positive': "green",
                                 'Neutral': px.colors.qualitative.Pastel[10],
                                 'Negative': "crimson"},
            hole=.5).update_traces(textposition='inside', 
            textinfo='percent+label').update_layout(font={'family': 'verdana','size':8}, 
            margin={'t': 10,"b": 10, "r": 0, "l":0},legend={'font':{'size':5.5},
            'orientation':'v','yanchor':'bottom','y':0.01,'xanchor':'right','x':1})
    )

# News & Twitter wordcloud
def generate_wordcloud(data):

    image = Image.open("circle_mask.png")
    mask = np.array(image)
    wc = WordCloud(background_color='white', mask = mask, width=290, height=227)
    wc.fit_words(data)
    
    img = BytesIO()
    wc.to_image().save(img, format='PNG')
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())

# News & Twitter Top 10 words bargraph
def generate_graph(topword_df):
    topword_df = topword_df.sort_values(by=['count'])
    return dcc.Graph(
        figure={
            "data": [go.Bar(
                x = topword_df["count"],
                y = topword_df["word"],
                text = topword_df["count"],
                textposition = 'auto',
                orientation="h",
                hovertemplate = '"%{y}", %{x} times<extra></extra>',
                marker_color='#7791d1'
            )],
            "layout": go.Layout(
                hovermode='closest',
                margin={'t': 10,"b": 20, "r": 5},
                font_family='verdana',
                font_color='darkblue',
                font_size= 10,
                width=290,
                height=495
            )
        },
        config={'displayModeBar': False}
    )

# Twitter Timeseries
def generate_timeseries(timeseries_df):
    fig = px.line(timeseries_df, x='Date_Time', y='Sentiment', width=615, height=225)
    fig.update_layout(font={'family': 'verdana','color':'darkblue','size':10},margin={'t': 5,'b': 5, 'r': 5, 'l':5}, 
    xaxis_title='Time', yaxis_title='Sentiment',plot_bgcolor = '#EAECEE')
    return fig

# App layout 2 with tabs (below)
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

app.layout = html.Div([

    # Part 1: Search Row
    dbc.Row([
        dbc.Col([
            html.H5("Search Keyword:", style={"margin-bottom":5,"margin-top":5, "margin-left":20,'font-family': 'verdana','font-size':15,'height':20,'width':140,'textAlign': 'left','color': 'white'}),   
        ],width=1.5),
        dbc.Col([
            html.Div([
                dcc.Input(id="keyword", type="text", placeholder="E.g. Apple", style={"margin-bottom":5,"margin-top":5}),
                dbc.Button("Search", color="dark",size="sm", id="search_button",n_clicks=0, className="mr-1"),
            ],className="search_style"),
            html.P(id = "search_datetime"),],
            width=3),
        dbc.Col([
            html.Div(html.P(id = "price_date"),style={'color': 'white'}),],
            width=6),
    ],style={"height":40,'backgroundColor': "#20315A"}), 

    html.Br(),

    html.Div([
        dcc.Tabs(children=[

            # Part 2: News content
            dcc.Tab(label='News',
                    children=[
                            dbc.Row([
                                    html.H5("Select News Source:", style={"margin-bottom":5,"margin-top":5, 'font-family': 'verdana','font-size':15,'height':20,'width':180,'textAlign': 'left','color': 'black','margin-left':20}), 
                                    html.Div(
                                        dcc.Dropdown(
                                            id='sources_dropdown', 
                                            options=[{'label': i['source name'], 'value': i['source']} for i in get_sources()],
                                            value="bloomberg",
                                            style={"height:":30,'width':250},
                                            placeholder="Select Source"))
                            ],style={"margin-top":5}), 

                        dbc.Row([
                            dbc.Col(html.H5("News Today", style={'font-family': 'verdana','font-size':16,'height':20,'textAlign': 'center','color': 'white','backgroundColor': "#20315A","margin-top":5}),
                            width=6,style={'margin-left':5}),

                            dbc.Col(html.H5("Sentiment Breakdown", style={'font-family': 'verdana','font-size':16,'height':20,'textAlign': 'center','color': 'white','backgroundColor': "#20315A","margin-top":5}),
                            width=3),

                            dbc.Col(html.H5("Top 10 Mentioned Words", style={'font-family': 'verdana','font-size':16,'height':20,'textAlign': 'center','color': 'white','backgroundColor': "#20315A","margin-top":5,"width":300}),
                            width=2.5),
                        ]),
                            
                            dbc.Row([

                                # Part 2.1: News table
                                dbc.Col(html.Div([
                                    news_table_header,
                                    html.Div(id="news_table"),
                                ]), 
                                width=6,style={'margin-left':5}),

                                dbc.Col(html.Div([
                                    
                                    # Part 2.2: News piechart
                                    html.Div(id="news_piechart"),

                                    html.H5("Wordcloud", style={'font-family': 'verdana','font-size':16,'height':20,'textAlign': 'center','color': 'white','backgroundColor': "#20315A","margin-top":5}),

                                    # Part 2.3: News wordcloud
                                    html.Img(id="news_wordcloud")

                                    ]),        
                                width=3),

                                # Part 2.4: News bargraph
                                dbc.Col(html.Div(id="news_graph"),
                                width=2.8),
                            ]),
                    ],
                    style=tab_style, 
                    selected_style=tab_selected_style
                    ),

            # Part 3: Twitter content
            dcc.Tab(label='Twitter',
                    children=[
                        dbc.Row([
                            dbc.Col(html.H5("Tweets Today", style={'font-family': 'verdana','font-size':16,'height':20,'textAlign': 'center','color': 'white','backgroundColor': "#20315A","margin-top":5}),
                            width=6,style={'margin-left':5}),

                            dbc.Col(html.H5("Sentiment Breakdown", style={'font-family': 'verdana','font-size':16,'height':20,'textAlign': 'center','color': 'white','backgroundColor': "#20315A","margin-top":5}),
                            width=3),

                            dbc.Col(html.H5("Top 10 Mentioned Words", style={'font-family': 'verdana','font-size':16,'height':20,'textAlign': 'center','color': 'white','backgroundColor': "#20315A","margin-top":5,"width":300}),
                            width=2.5),
                        ]),

                        dbc.Row([
                            dbc.Col([
                                
                                # Part 3.1: Twitter timeseries
                                dcc.Loading(
                                    type="default",
                                    children=dcc.Graph(id='twitter_timeseries',style={'margin-bottom':5})
                                ),
                                
                                dcc.Tabs(
                                id="tabs",
                                children=[

                                    # Part 3.2: Twitter popular table
                                    dcc.Tab(
                                        label="Popular",
                                        children=html.Div([
                                            twitter_table_header,
                                            html.Div(id="twitter_table_popular"),
                                        ]),
                                        style=tab_style, 
                                        selected_style=tab_selected_style
                                    ),

                                    # Part 3.3: Twitter recent table
                                    dcc.Tab(
                                        label="Recent",
                                        children=html.Div([
                                            twitter_table_header,
                                            html.Div(id="twitter_table_recent"),
                                        ]),
                                        style=tab_style, 
                                        selected_style=tab_selected_style
                                    ),
                                ],
                                style={'font-size': 13,'height':30},
                            ),],
                            width=6,style={'margin-left':5}),

                            dbc.Col(html.Div([
                                
                                # Part 3.4: Twitter piechart
                                html.Div(id="twitter_piechart"),

                                html.H5("Wordcloud", style={'font-family': 'verdana','font-size':16,'height':20,'textAlign': 'center','color': 'white','backgroundColor': "#20315A","margin-top":5}),

                                # Part 3.5: Twitter wordcloud
                                html.Img(id="twitter_wordcloud")

                                ]),        
                            width=3),

                            # Part 3.5: Twitter bargraph
                            dbc.Col(html.Div(id="twitter_graph"),
                            width=2.8),
                        ]),

                        html.Br(),
                    ],
                    style=tab_style, 
                    selected_style=tab_selected_style
            ),
        ]),
    ],style={'padding-bottom':50,'backgroundColor': "#7791d1"}),
],style={'backgroundColor': "#4665AE"})

# Callbacks (below)
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Callback for News and Twitter tabs altogether
@app.callback(
               # Callback's outputs of News items
               [Output("news_table", "children"),
               Output("news_graph", "children"),
               Output("news_piechart", "children"),
               Output("news_wordcloud", "src"),
               
               # Callback's outputs of Twitter items
               Output("twitter_table_popular", "children"),
               Output("twitter_table_recent", "children"),
               Output("twitter_graph", "children"),
               Output("twitter_wordcloud", "src"),
               Output("twitter_piechart", "children"),

               # Callback's outputs of search input datetime
               Output("search_datetime","children")
               ],
               
               # Callback's inputs
               [Input("search_button","n_clicks"),
               Input("sources_dropdown","value")],
               [State("keyword","value")]
)

def update_page(search_click,source,search_input):

    if search_input:
        #News
        common_news_df = get_everything(search_input, source)
        news_df = common_news_df[['title', 'url', 'urlToImage', 'sentiment', 'date']][0:15]
        news_topword_df = news_top_mentioned(common_news_df, search_input)[0:10]
        news_wordcloud_dict = dict(sorted(news_top_mentioned(common_news_df, search_input).values.tolist()))
        news_piechart_df = news_overallsentiment(common_news_df)

        #Twitter
        common_twitter_df = tweet_search(search_input, 'popular')
        popular_twitter_df = common_twitter_df[['Tweets', 'Sentiment', 'url', 'date']][0:15]
        recent_twitter_df = tweet_search(search_input, 'recent')[['Tweets', 'Sentiment', 'url', 'date']][0:15]
        twitter_topword_df = twt_top_mentioned(common_twitter_df, 'stock')[0:10]
        twitter_wordcloud_dict = dict(sorted(twt_top_mentioned(common_twitter_df, 'stock').values.tolist()))
        twitter_piechart_df = overallsentiment(common_twitter_df)

    elif source:
        #News
        common_news_df = get_everything('', source)
        news_df = common_news_df[['title', 'url', 'urlToImage', 'sentiment','date']][0:15]
        news_topword_df = news_top_mentioned(common_news_df, '')[0:10]
        news_wordcloud_dict = dict(sorted(news_top_mentioned(common_news_df, '').values.tolist()))
        news_piechart_df = news_overallsentiment(common_news_df)

        #Twitter
        common_twitter_df = tweet_search('stock', 'popular')
        popular_twitter_df = common_twitter_df[['Tweets', 'Sentiment', 'url', 'date']][0:15]
        recent_twitter_df = tweet_search('stock', 'recent')[['Tweets', 'Sentiment', 'url', 'date']][0:15]
        twitter_topword_df = twt_top_mentioned(common_twitter_df, 'stock')[0:10]
        twitter_wordcloud_dict = dict(sorted(twt_top_mentioned(common_twitter_df, 'stock').values.tolist()))
        twitter_piechart_df = overallsentiment(common_twitter_df)

    #Empty dropdown handling
    else:
        #News
        common_news_df = get_everything('', 'bloomberg')
        news_df = common_news_df[['title', 'url', 'urlToImage', 'sentiment','date']][0:15]
        news_topword_df = news_top_mentioned(common_news_df, '')[0:10]
        news_wordcloud_dict = dict(sorted(news_top_mentioned(common_news_df, '').values.tolist()))
        news_piechart_df = news_overallsentiment(common_news_df)

        #Twitter
        common_twitter_df = tweet_search('stock', 'popular')
        popular_twitter_df = common_twitter_df[['Tweets', 'Sentiment', 'url', 'date']][0:15]
        recent_twitter_df = tweet_search('stock', 'recent')[['Tweets', 'Sentiment', 'url', 'date']][0:15]
        twitter_topword_df = twt_top_mentioned(common_twitter_df, 'stock')[0:10]
        twitter_wordcloud_dict = dict(sorted(twt_top_mentioned(common_twitter_df, 'stock').values.tolist()))
        twitter_piechart_df = overallsentiment(common_twitter_df)

    #Search Input datetime
    datetime_of_search = datetime.now()
    datetime_of_search = str(datetime_of_search).split(".")
    datetime_of_search = "Last updated: " + datetime_of_search[0].replace(' ',', ')

    return [ 
        # Return News items 
        [generate_news_table(news_df,source)] , 
        [generate_graph(news_topword_df)] ,  
        [generate_piechart(news_piechart_df)] ,  
        generate_wordcloud(news_wordcloud_dict) , 

        # Return Twitter items
        [generate_twitter_table(popular_twitter_df)] ,
        [generate_twitter_table(recent_twitter_df)] ,
        [generate_graph(twitter_topword_df)] , 
        generate_wordcloud(twitter_wordcloud_dict) , 
        [generate_piechart(twitter_piechart_df)] ,

        # Search input datetime
        [datetime_of_search]
    ]

# Callback for Timeseries
@app.callback(
               # Callback's outputs of Twitter time series
               [Output("twitter_timeseries", "figure")],
               
               # Callback's inputs
               [Input("search_button","n_clicks")],
               [State("keyword","value")],
)

def update_timeseries(search_click,search_input):

    if search_input:
        #Twitter
        twitter_timeseries_df = time_series(search_input)

    #Empty search_input handling
    else:
        #Twitter
        twitter_timeseries_df = time_series('stock')[0:9]

    return [ generate_timeseries(twitter_timeseries_df) ]

# Run server (below)
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)