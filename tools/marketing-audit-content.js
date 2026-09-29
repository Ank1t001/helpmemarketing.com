/* HelpMeMarketing marketing check-up: content (v2, 2026-09-29).
 * Data only. Behaviour lives in /tools/marketing-audit.js.
 * Plain words on purpose: a 5th grader should follow every line. No em or en dashes.
 * An option with unsure:true counts as "not known yet" and adds its question's verify line.
 * An option's p map raises priorities: { PRIORITY_ID: 1 (some problem) or 2 (big problem) }.
 */
window.HMM_AUDIT = (function () {
  var NS = { v: 'unsure', label: 'I’m not sure', unsure: true };

  var shared = [
    { id: 'buy', short: 'How customers buy', q: 'How do customers usually buy from you?',
      hint: 'If you sell in more than one way, pick the one that brings in the most money.',
      opts: [
        { v: 'online', label: 'They buy online', sum: 'Customers buy online' },
        { v: 'appointment', label: 'They book an appointment', sum: 'Customers book an appointment' },
        { v: 'enquiry', label: 'They send an enquiry or ask for a quote', sum: 'Customers send an enquiry or ask for a quote' },
        { v: 'other', label: 'Another way', sum: 'Customers buy another way' }
      ] },
    { id: 'goal', short: 'Your goal', q: 'What would you most like to improve?',
      opts: [
        { v: 'more', label: 'Get more customers', sum: 'More customers' },
        { v: 'quality', label: 'Get better enquiries', sum: 'Better enquiries' },
        { v: 'convert', label: 'Win more sales from the enquiries I already get', sum: 'More sales from the enquiries you already get' },
        { v: 'repeat', label: 'Get more repeat business', sum: 'More repeat business' },
        { v: 'clarity', label: 'Know what my marketing is really doing', sum: 'Clear results from your marketing' }
      ] },
    { id: 'stage', short: 'Where you are today', q: 'Where is your business today?',
      opts: [
        { v: 'launch', label: 'Getting ready to launch', sum: 'Getting ready to launch' },
        { v: 'limited', label: 'Open, doing a little marketing', sum: 'Open, doing a little marketing' },
        { v: 'active', label: 'Open, marketing actively', sum: 'Open, marketing actively' }
      ] }
  ];

  var capability = { id: 'who', short: 'Who makes changes', q: 'Who would usually make these changes?',
    hint: 'This changes how we write your plan. It does not sign you up for anything.',
    opts: [
      { v: 'self', label: 'I would', sum: 'You would' },
      { v: 'team', label: 'My internal team', sum: 'Your internal team' },
      { v: 'agency', label: 'My agency or freelancer', sum: 'Your agency or freelancer' },
      { v: 'help', label: 'I need help deciding', sum: 'Not decided yet' }
    ] };

  var paths = {
    online: {
      name: 'Online purchases', intro: 'Now a few questions about how people shop with you.',
      key: ['o_visits', 'o_cart', 'o_checkout'], find: 'P_SHOP_FIND', fallback: 'P_REACH',
      order: ['P_CHECKOUT', 'P_PRODUCT', 'P_REACH', 'P_REPEAT'],
      boost: { more: ['P_REACH'], convert: ['P_CHECKOUT', 'P_PRODUCT'], quality: ['P_PRODUCT'] },
      qs: [
        { id: 'o_visits', short: 'Visits to product pages', q: 'Do enough people visit your product pages?',
          verify: 'Check how many people visited your product pages last month. Your shop’s reports show this.',
          opts: [
            { v: 'plenty', label: 'Yes, plenty' },
            { v: 'some', label: 'Some, but fewer than I want', p: { P_REACH: 1 } },
            { v: 'few', label: 'Very few', p: { P_REACH: 2 } }, NS ] },
        { id: 'o_cart', short: 'Adding to cart', q: 'Do visitors add products to their cart?',
          verify: 'Check how many visitors added something to their cart last month.',
          opts: [
            { v: 'often', label: 'Yes, often' },
            { v: 'some', label: 'Some do, most do not', p: { P_PRODUCT: 1 } },
            { v: 'rare', label: 'Hardly ever', p: { P_PRODUCT: 2 } }, NS ] },
        { id: 'o_checkout', short: 'Finishing checkout', q: 'Do people who start checkout finish paying?',
          verify: 'Check how many people started checkout and how many finished paying.',
          opts: [
            { v: 'most', label: 'Most of them finish' },
            { v: 'many-stop', label: 'Many stop before paying', p: { P_CHECKOUT: 2 } }, NS ] },
        { id: 'o_track', short: 'Seeing which ads or posts bring sales', q: 'Can you see which ads or posts bring in sales?',
          verify: 'Place a test order and check it shows up once in your website stats, with the right amount.',
          opts: [
            { v: 'yes', label: 'Yes, clearly' },
            { v: 'rough', label: 'Only roughly', unsure: true },
            { v: 'no', label: 'No, I can’t tell', unsure: true } ] },
        { id: 'o_repeat', short: 'Buying again', q: 'Do customers buy from you again?',
          verify: 'Count how many of last year’s customers bought more than once.',
          opts: [
            { v: 'often', label: 'Yes, often' },
            { v: 'sometimes', label: 'Sometimes' },
            { v: 'rarely', label: 'Rarely', p: { P_REPEAT: 1 } },
            { v: 'once', label: 'My product is usually a one-time buy' }, NS ] }
      ]
    },

    appointments: {
      name: 'Appointments', intro: 'Now a few questions about how people book and visit.',
      key: ['a_fit', 'a_finish', 'a_noshow'], find: 'P_APPT_FIND', fallback: 'P_REACH',
      order: ['P_NOSHOW', 'P_BOOKING', 'P_FIT', 'P_REACH'],
      boost: { more: ['P_REACH', 'P_BOOKING'], quality: ['P_FIT'], convert: ['P_BOOKING', 'P_NOSHOW'] },
      qs: [
        { id: 'a_fit', short: 'Good-fit enquiries', q: 'Are most people who contact you a good fit for what you offer?',
          verify: 'For the next 2 weeks, mark each new enquiry as a good fit or not.',
          opts: [
            { v: 'most', label: 'Yes, most are' },
            { v: 'half', label: 'About half', p: { P_FIT: 1 } },
            { v: 'few', label: 'Most are not', p: { P_FIT: 2 } }, NS ] },
        { id: 'a_wait', short: 'Wait for a first visit', q: 'How soon can a new customer get a first visit?',
          verify: 'Check the first open time for a new customer this week.',
          opts: [
            { v: 'week', label: 'Within a week' },
            { v: 'weeks', label: 'In 1 to 3 weeks', p: { P_BOOKING: 1 } },
            { v: 'long', label: 'Longer than 3 weeks', p: { P_BOOKING: 2 } }, NS ] },
        { id: 'a_how', short: 'How people book', q: 'How do people book with you?',
          opts: [
            { v: 'online', label: 'Online, any time' },
            { v: 'call', label: 'Only by phone, email or message', p: { P_BOOKING: 1 } } ] },
        { id: 'a_finish', short: 'Finishing a booking', q: 'Do people who start to book finish it?',
          verify: 'Try booking as a new customer on your phone, then check how many started and finished last month.',
          opts: [
            { v: 'most', label: 'Most of them do' },
            { v: 'many-stop', label: 'Many stop partway', p: { P_BOOKING: 2 } }, NS ] },
        { id: 'a_remind', short: 'Confirmations and reminders', q: 'Do you send a confirmation and a reminder before each visit?',
          verify: 'Book a test visit and see which messages arrive, and when.',
          opts: [
            { v: 'both', label: 'Yes, both' },
            { v: 'confirm', label: 'Only a confirmation', p: { P_NOSHOW: 1 } },
            { v: 'none', label: 'Neither', p: { P_NOSHOW: 1 } }, NS ] },
        { id: 'a_noshow', short: 'Missed visits', q: 'How many people miss their visit without telling you?',
          verify: 'Count the missed visits over the next 4 weeks.',
          opts: [
            { v: 'few', label: 'Hardly any (fewer than 1 in 20)' },
            { v: 'some', label: 'Some (about 1 in 10)', p: { P_NOSHOW: 1 } },
            { v: 'many', label: 'Many (1 in 5 or more)', p: { P_NOSHOW: 2 } }, NS ] }
      ]
    },

    enquiries: {
      name: 'Enquiries and quotes', intro: 'Now a few questions about your enquiries and quotes.',
      key: ['e_fit', 'e_reply', 'e_meet'], find: 'P_ENQ_FIND', fallback: 'P_REACH',
      order: ['P_CLOSE', 'P_FOLLOWUP', 'P_FIT', 'P_REACH'],
      boost: { more: ['P_REACH'], quality: ['P_FIT'], convert: ['P_FOLLOWUP', 'P_CLOSE'] },
      qs: [
        { id: 'e_source', short: 'Where enquiries come from', q: 'Do you know where your enquiries come from?',
          verify: 'Ask every new enquiry: “How did you find us?” and write it down.',
          opts: [
            { v: 'most', label: 'Yes, for most of them' },
            { v: 'some', label: 'For some of them', unsure: true },
            { v: 'no', label: 'No', unsure: true } ] },
        { id: 'e_fit', short: 'Good-fit enquiries', q: 'How many enquiries are a good fit for you?',
          verify: 'For the next 4 weeks, mark each new enquiry as a good fit or not.',
          opts: [
            { v: 'most', label: 'Most of them' },
            { v: 'half', label: 'About half', p: { P_FIT: 1 } },
            { v: 'few', label: 'Only a few', p: { P_FIT: 2 } }, NS ] },
        { id: 'e_reply', short: 'Reply speed', q: 'How fast do you usually reply to a new enquiry?',
          verify: 'For your last 10 enquiries, write down how long each one waited for a reply.',
          opts: [
            { v: 'same', label: 'The same business day' },
            { v: 'days', label: 'Within 2 or 3 days', p: { P_FOLLOWUP: 1 } },
            { v: 'missed', label: 'It depends, and some get missed', p: { P_FOLLOWUP: 2 } }, NS ] },
        { id: 'e_meet', short: 'Enquiries that become a call or meeting', q: 'Do good enquiries turn into a call or meeting?',
          verify: 'Count how many good enquiries last month became a call or meeting.',
          opts: [
            { v: 'most', label: 'Most do' },
            { v: 'some', label: 'Some do', p: { P_FOLLOWUP: 1 } },
            { v: 'few', label: 'Few do', p: { P_FOLLOWUP: 1, P_CLOSE: 1 } }, NS ] },
        { id: 'e_quote', short: 'Quote follow-up', q: 'After you send a quote, what happens?',
          opts: [
            { v: 'chase', label: 'We follow up until we get a yes or no' },
            { v: 'once', label: 'We follow up once', p: { P_CLOSE: 1 } },
            { v: 'wait', label: 'We wait for them to reply', p: { P_CLOSE: 2 } },
            { v: 'none', label: 'We don’t send quotes' } ] },
        { id: 'e_lost', short: 'Why you lose work', q: 'Do you know why you lose work?',
          verify: 'Ask the next 3 people who say no for the main reason.',
          opts: [
            { v: 'yes', label: 'Yes, we ask' },
            { v: 'guess', label: 'We have a guess', unsure: true },
            { v: 'no', label: 'No idea', unsure: true, p: { P_CLOSE: 1 } } ] }
      ]
    },

    repeat: {
      name: 'Repeat business', intro: 'Now a few questions about customers coming back.',
      key: ['r_back'], find: 'P_REPEAT_FIND', fallback: 'P_REFERRAL',
      order: ['P_REFERRAL', 'P_REPEAT', 'P_REACTIVATE'],
      boost: {},
      qs: [
        { id: 'r_need', short: 'Would they buy again', q: 'Would a happy customer normally buy from you again?',
          opts: [
            { v: 'often', label: 'Yes, often (every few months or more)' },
            { v: 'yearly', label: 'Yes, now and then (about once a year)' },
            { v: 'once', label: 'Not really, most only need us once', p: { P_REFERRAL: 3 } } ] },
        { id: 'r_back', short: 'How many come back', q: 'How many of your customers come back?',
          verify: 'Count how many of last year’s customers bought or visited more than once.',
          when: function (a) { return a.r_need !== 'once'; },
          opts: [
            { v: 'most', label: 'Most of them' },
            { v: 'some', label: 'Some of them', p: { P_REPEAT: 1, P_REACTIVATE: 1 } },
            { v: 'few', label: 'Very few', p: { P_REPEAT: 1, P_REACTIVATE: 2 } }, NS ] },
        { id: 'r_list', short: 'Customer contact list', q: 'Do you keep customers’ contact details, with permission to contact them?',
          verify: 'Check how many of last year’s customers you could email or text today.',
          opts: [
            { v: 'yes', label: 'Yes, for most customers' },
            { v: 'some', label: 'For some of them', p: { P_REPEAT: 1 } },
            { v: 'no', label: 'No', p: { P_REPEAT: 2 } } ] },
        { id: 'r_follow', short: 'Contact after buying', q: 'Do you contact customers after they buy?',
          opts: [
            { v: 'plan', label: 'Yes, we have a planned follow-up' },
            { v: 'news', label: 'Now and then, when we have news', p: { P_REPEAT: 1 } },
            { v: 'no', label: 'No', p: { P_REPEAT: 2 } } ] },
        { id: 'r_reason', short: 'A reason to come back', q: 'Do customers have a clear reason to come back?',
          when: function (a) { return a.r_need !== 'once'; },
          opts: [
            { v: 'yes', label: 'Yes, like a refill, a service that is due, or new stock' },
            { v: 'maybe', label: 'Maybe, we haven’t thought about it', p: { P_REPEAT: 1 } },
            { v: 'no', label: 'No', p: { P_REPEAT: 1 } } ] }
      ]
    },

    prelaunch: {
      name: 'Getting ready to launch', intro: 'Now a few questions about what is ready before you launch.',
      key: [], find: 'P_LAUNCH_GO', fallback: 'P_LAUNCH_GO',
      order: ['P_LAUNCH_WHO', 'P_LAUNCH_OFFER', 'P_LAUNCH_ROUTE', 'P_LAUNCH_READY', 'P_LAUNCH_TRACK', 'P_LAUNCH_GO'],
      boost: {},
      qs: [
        { id: 'l_who', short: 'Your first customer', q: 'Can you describe your first customer in one sentence?',
          opts: [
            { v: 'yes', label: 'Yes, clearly' },
            { v: 'rough', label: 'Roughly', p: { P_LAUNCH_WHO: 1 } },
            { v: 'no', label: 'Not yet', p: { P_LAUNCH_WHO: 2 } } ] },
        { id: 'l_offer', short: 'Your offer and price', q: 'Can you say what you sell, the price, and why people should pick you?',
          opts: [
            { v: 'yes', label: 'Yes' },
            { v: 'part', label: 'Partly', p: { P_LAUNCH_OFFER: 1 } },
            { v: 'no', label: 'Not yet', p: { P_LAUNCH_OFFER: 2 } } ] },
        { id: 'l_route', short: 'A way to buy, book or enquire', q: 'Can a customer buy, book or enquire with you today?',
          opts: [
            { v: 'tested', label: 'Yes, and we have tested it' },
            { v: 'untested', label: 'It is set up, but not tested', p: { P_LAUNCH_ROUTE: 1 } },
            { v: 'no', label: 'Not yet', p: { P_LAUNCH_ROUTE: 2 } } ] },
        { id: 'l_ready', short: 'Ready to serve customers', q: 'If 20 customers came next week, could you serve them well?',
          opts: [
            { v: 'yes', label: 'Yes' },
            { v: 'some', label: 'Some of them', p: { P_LAUNCH_READY: 1 } },
            { v: 'no', label: 'Not yet', p: { P_LAUNCH_READY: 2 } } ] },
        { id: 'l_track', short: 'Knowing where customers come from', q: 'Will you know where your first customers came from?',
          opts: [
            { v: 'yes', label: 'Yes, it is set up' },
            { v: 'ask', label: 'We will ask them', p: { P_LAUNCH_TRACK: 1 } },
            { v: 'no', label: 'Not yet', p: { P_LAUNCH_TRACK: 2 } } ] }
      ]
    },

    measure: {
      name: 'Knowing what works', intro: 'Now a few questions about your results and reports.',
      key: ['m_what'], find: 'P_RECORD', fallback: 'P_REACH',
      order: ['P_RECORD', 'P_REPORTS', 'P_REACH'],
      boost: { clarity: ['P_REPORTS', 'P_RECORD'], more: ['P_REACH'] },
      qs: [
        { id: 'm_reports', short: 'Marketing reports', q: 'Do you get marketing reports?',
          opts: [
            { v: 'regular', label: 'Yes, regularly' },
            { v: 'sometimes', label: 'Sometimes', p: { P_REPORTS: 1 } },
            { v: 'no', label: 'No', p: { P_REPORTS: 1 } } ] },
        { id: 'm_what', short: 'What the reports show', q: 'What do the reports mostly show?',
          verify: 'Open your last report and circle any number that is a sale, a booking or an enquiry.',
          when: function (a) { return a.m_reports && a.m_reports !== 'no'; },
          opts: [
            { v: 'results', label: 'Sales, bookings or enquiries' },
            { v: 'activity', label: 'Clicks, views and likes', p: { P_REPORTS: 2 } }, NS ] },
        { id: 'm_log', short: 'Writing down each sale or enquiry', q: 'Do you write down every new sale or enquiry?',
          opts: [
            { v: 'all', label: 'Yes, every one' },
            { v: 'some', label: 'Some of them', p: { P_RECORD: 1 } },
            { v: 'no', label: 'No', p: { P_RECORD: 2 } } ] },
        { id: 'm_source', short: 'Where customers found you', q: 'Do you know where each customer found you?',
          opts: [
            { v: 'most', label: 'Yes, for most of them' },
            { v: 'some', label: 'For some of them', p: { P_RECORD: 1 } },
            { v: 'no', label: 'No', p: { P_RECORD: 2 } } ] },
        { id: 'm_act', short: 'Changes made from reports', q: 'In the last 3 months, did you change anything because of a report?',
          when: function (a) { return a.m_reports && a.m_reports !== 'no'; },
          opts: [
            { v: 'yes', label: 'Yes' },
            { v: 'no', label: 'No', p: { P_REPORTS: 1 } },
            { v: 'cant', label: 'The reports don’t help me decide', p: { P_REPORTS: 2 } } ] }
      ]
    }
  };

  /* Which path a visitor follows, from the three shared answers. */
  function pathFor(a) {
    if (a.stage === 'launch') return 'prelaunch';
    if (a.goal === 'clarity') return 'measure';
    if (a.goal === 'repeat') return 'repeat';
    if (a.buy === 'online') return 'online';
    if (a.buy === 'appointment') return 'appointments';
    if (a.buy === 'enquiry') return 'enquiries';
    return 'measure';
  }

  var OWN = {
    boss: 'The owner or manager', desk: 'Whoever answers enquiries or bookings', site: 'Whoever looks after the website',
    shop: 'Whoever looks after the online store', mkt: 'Whoever runs your marketing', sales: 'Whoever handles sales',
    report: 'Whoever sends your marketing reports'
  };

  var priorities = {
    P_SHOP_FIND: {
      title: 'Find out where shoppers stop', area: 'Finding where shoppers leave',
      plain: 'Before you change anything, find the step where most shoppers give up. Then you fix the right thing.',
      because: 'Some of your answers were “not sure”, so the safest first step is to find out, not to guess.',
      actions: [
        { do: 'Write down last month’s number for each shopping step.', how: 'Open your shop’s reports (Shopify, WooCommerce or similar). Write down store visits, product page views, add to carts, checkouts started and orders.', owner: OWN.shop },
        { do: 'Find the step with the biggest drop.', how: 'Compare each number with the one before it. The biggest drop is where to look first.', owner: OWN.shop },
        { do: 'Buy something from your own store on your phone.', how: 'Start from Google or an ad and go all the way to paying. Note anything slow, confusing or surprising, like extra fees.', owner: OWN.boss }
      ],
      measure: 'Out of every 100 visitors, how many buy something?', review: 'in 4 weeks',
      review_list: ['Numbers written down for all five steps', 'Biggest drop found', 'Test order done on a phone', 'One change picked for the biggest drop'],
      agency: ['How many visits, add to carts, checkouts and orders did we have last month?', 'At which step do we lose the most shoppers?', 'Is every purchase tracked, and how do you know?'],
      evidence: ['A screenshot of last month’s shopping funnel or sales report', 'A list of the tracking set up on the site'],
      help: 'Someone who can read your store’s reports and check your purchase tracking. Usually a few hours of work.',
      topic: 'finding where shoppers leave your online store', resource: 'R_SHOP'
    },
    P_CHECKOUT: {
      title: 'Help more shoppers finish paying', area: 'Checkout',
      plain: 'People want what you sell, but something at checkout stops them. Small fixes here often bring the fastest wins.',
      because: 'Shoppers get to checkout and then leave. That is the step closest to the money.',
      actions: [
        { do: 'Do a test checkout on your phone and write down every problem.', how: 'Count the steps and boxes to fill in. Note surprise costs, a forced sign-up, slow pages and missing ways to pay.', owner: OWN.shop },
        { do: 'Show shipping cost and delivery time before checkout.', how: 'Put them on the product page and in the cart. Surprise costs are the most common reason people leave.', owner: OWN.shop },
        { do: 'Remove one thing that slows people down.', how: 'For example, allow checkout without an account, add Apple Pay or Google Pay, or cut boxes you do not need.', owner: OWN.shop }
      ],
      measure: 'Out of every 10 people who start checkout, how many finish paying?', review: '2 weeks after your change',
      review_list: ['Test checkout done on a phone', 'Shipping cost shown before checkout', 'One slowdown removed', 'Finish rate written down before and after'],
      agency: ['How many people started checkout last month, and how many finished?', 'What are the top reasons people leave at checkout?', 'What would you change first, and why?'],
      evidence: ['The checkout drop-off report for the last 30 days', 'A screen recording of the checkout on a phone'],
      help: 'Someone who knows your shop platform and can change checkout settings. Often a small, one-time job.',
      topic: 'helping more shoppers finish checkout', resource: 'R_SHOP'
    },
    P_PRODUCT: {
      title: 'Make your product pages easier to say yes to', area: 'Product pages',
      plain: 'People look at your products but do not add them to the cart. The page may not answer their questions.',
      because: 'Visitors see your products, but few add them to the cart.',
      actions: [
        { do: 'Read the pages for your top 3 products as if you were a new customer.', how: 'Ask: Is the price clear? Is it clear who it is for? Are there real photos, reviews, sizes and delivery details?', owner: OWN.boss },
        { do: 'Add the missing answers near the Add to cart button.', how: 'Add reviews, clear photos, a short list of what it does for them, and delivery and returns details.', owner: OWN.shop },
        { do: 'Ask 3 recent customers what almost stopped them buying.', how: 'Email or call them. Use their own words on the page.', owner: OWN.boss }
      ],
      measure: 'Out of every 100 people who see a product page, how many add it to the cart?', review: 'in 4 weeks',
      review_list: ['Top 3 product pages checked', 'Reviews and delivery details near the button', 'Customer words added to the page', 'Add-to-cart rate written down before and after'],
      agency: ['What share of product page visitors add to cart, for our top 3 products?', 'What do visitors do on the page before they leave?', 'Which page changes would you test first?'],
      evidence: ['Add-to-cart rate by product for the last 30 days', 'Any heatmaps or session recordings of the product pages'],
      help: 'Someone who can write clear product pages and set up simple tests.',
      topic: 'turning more product page visits into sales', resource: 'R_SHOP'
    },
    P_REACH: {
      title: 'Reach more of the right people', area: 'Getting found',
      plain: 'The steps after someone finds you look healthy. Now the job is to bring in more of the right people, using what already works.',
      because: 'Your answers do not show a big leak later on, so more of the right people finding you is the next step.',
      actions: [
        { do: 'List where your last 20 customers came from.', how: 'Use your records, or ask them. Group them: Google search, ads, social media, referral, walk-in, other.', owner: OWN.boss },
        { do: 'Pick the one place that brought your best customers.', how: 'Best means they bought, paid well and were good to work with. Not just the most of them.', owner: OWN.boss },
        { do: 'Put a little more time or money into that one place for 30 days.', how: 'Change only one thing at a time, so you can see what worked.', owner: OWN.mkt }
      ],
      measure: 'New customers each month from the place you picked.', review: 'in 30 days',
      review_list: ['Source of the last 20 customers listed', 'Best source picked', 'One 30-day test started', 'New customers counted at the end'],
      agency: ['Which source brought our best customers in the last 3 months?', 'What would you do with a bit more budget on that source?', 'How will we know in 30 days if it worked?'],
      evidence: ['New customers by source for the last 3 months', 'Cost per new customer by source, where you spend money'],
      help: 'Someone who can run one channel well, like Google Ads, search (SEO) or social media, and report on new customers.',
      topic: 'bringing in more of the right customers', resource: 'R_REACH'
    },
    P_APPT_FIND: {
      title: 'Find out where bookings are lost', area: 'Finding where bookings are lost',
      plain: 'Before you change anything, follow each enquiry from first contact to the visit. Then you can see where people drop out.',
      because: 'Some of your answers were “not sure”, so the first job is to find out where people drop out.',
      actions: [
        { do: 'Start an enquiry tracker today.', how: 'One row per person: date, how they found you, good fit (yes or no), booked (yes or no), came (yes or no).', owner: OWN.desk },
        { do: 'Fill it in for 2 weeks without changing anything else.', how: 'Fill it in the same day. Count every enquiry, including calls and messages.', owner: OWN.desk },
        { do: 'Count where most people dropped out.', how: 'Compare enquiries, good fits, bookings and visits. The biggest drop is your next priority.', owner: OWN.boss }
      ],
      measure: 'Out of every 10 enquiries, how many come to a visit?', review: 'in 2 weeks',
      review_list: ['Tracker started', 'Every enquiry logged for 2 weeks', 'Biggest drop found', 'One next step picked'],
      agency: ['How many enquiries did your work bring last month, and how many booked?', 'Can you show bookings, not just clicks or calls?', 'Where do you think we lose people?'],
      evidence: ['Enquiries and bookings by source for last month', 'Call or form reports, if you have them'],
      help: 'Someone who can set up simple booking tracking and read it with you.',
      topic: 'finding where you lose bookings', resource: 'R_TRACKER'
    },
    P_NOSHOW: {
      title: 'Cut missed appointments', area: 'Missed appointments',
      plain: 'People book but do not show up. Each empty slot is time you cannot sell again. Clear confirmations and reminders help most.',
      because: 'Some people book but do not come, and your messages may not be doing enough to remind them.',
      actions: [
        { do: 'Send a confirmation right after every booking.', how: 'Include the date, time, address, how to get ready, and how to change the time.', owner: OWN.desk },
        { do: 'Send a reminder 1 day before, with an easy way to move the time.', how: 'A text message works best. An easy way to reschedule lets you fill the slot.', owner: OWN.desk },
        { do: 'Keep a short waitlist to fill slots that open up.', how: 'When someone cancels, offer the time to the first person on the list.', owner: OWN.desk }
      ],
      measure: 'Out of every 20 booked visits, how many people did not come?', review: 'in 4 weeks',
      review_list: ['Confirmation sent for every booking', 'Reminder sent 1 day before', 'Easy way to reschedule in the reminder', 'Missed visits counted each week'],
      agency: ['What confirmation and reminder messages go out today, and when?', 'Can people move their time without calling?', 'How many booked visits were missed last month?'],
      evidence: ['Copies of the confirmation and reminder messages', 'Missed-visit count from your booking system for the last 2 months'],
      help: 'Someone who can set up automatic messages in your booking system. Often a one-time job of a few hours.',
      topic: 'cutting missed appointments with better confirmations and reminders', resource: 'R_BOOKING'
    },
    P_BOOKING: {
      title: 'Make booking quick and easy', area: 'Booking',
      plain: 'People want to see you, but booking is slow or hard. Make it quick and simple, or they may go somewhere else.',
      because: 'Booking takes too long or is hard to finish.',
      actions: [
        { do: 'Try to book as a new customer on your phone.', how: 'Time it. Note every extra step, question or wait.', owner: OWN.boss },
        { do: 'Remove the biggest barrier you found.', how: 'For example, add online booking, show open times, reply to messages faster, or ask fewer questions.', owner: OWN.site },
        { do: 'Keep some time open for new customers if the wait is long.', how: 'Hold a few slots each week for new customers, or start a waitlist.', owner: OWN.boss }
      ],
      measure: 'Out of every 10 people who try to book, how many finish?', review: 'in 4 weeks',
      review_list: ['Test booking done on a phone', 'Biggest barrier removed', 'Wait for new customers checked', 'Finished bookings counted each week'],
      agency: ['How many people start booking online, and how many finish?', 'At which booking step do people stop?', 'What would you change first?'],
      evidence: ['Booking page visits and finished bookings for last month', 'A screen recording of booking on a phone'],
      help: 'Someone who knows your booking system and website. Usually a small setup job.',
      topic: 'making it easier for customers to book with you', resource: 'R_BOOKING'
    },
    P_FIT: {
      title: 'Attract more of the right customers', area: 'Enquiry quality',
      plain: 'Too many people who contact you are not a good fit. Clear messages help the right people come to you and the wrong ones look elsewhere.',
      because: 'Many of the people who contact you are not a good fit.',
      actions: [
        { do: 'Write down what makes a good customer and a poor fit.', how: 'Use the worksheet. Think about your 3 best and 3 worst recent customers.', owner: OWN.boss },
        { do: 'Check your website and ads against that list.', how: 'Do they say who you help, what you do not do, where you work, and a starting price or range?', owner: OWN.mkt },
        { do: 'Add 1 or 2 simple questions to your enquiry form.', how: 'For example, what they need and when. Keep the form short.', owner: OWN.site }
      ],
      measure: 'Out of every 10 enquiries, how many are a good fit?', review: 'in 4 weeks',
      review_list: ['Good fit and poor fit written down', 'Website and ads checked against it', 'Form questions added', 'Good-fit enquiries counted each week'],
      agency: ['Which ads, keywords or posts bring the most poor-fit enquiries?', 'Can we stop or change those?', 'How do you decide who we target?'],
      evidence: ['Enquiries by source, marked good fit or poor fit', 'The search terms or audiences behind recent enquiries'],
      help: 'Someone who can sharpen your message and who your ads reach. A marketing strategist or ads specialist.',
      topic: 'getting more of the right enquiries', resource: 'R_QUALIFY'
    },
    P_ENQ_FIND: {
      title: 'Find out where good enquiries are lost', area: 'Finding where enquiries are lost',
      plain: 'Follow each enquiry from first contact to won or lost for a few weeks. Then you know what to fix.',
      because: 'Some of your answers were “not sure”, so the first job is to find out where enquiries stop.',
      actions: [
        { do: 'Start an enquiry tracker today.', how: 'One row per enquiry: date, where they found you, good fit, date you replied, meeting, quote, won or lost, and why.', owner: OWN.desk },
        { do: 'Log every enquiry for 4 weeks.', how: 'Calls, emails, forms and messages. Fill it in the same day.', owner: OWN.desk },
        { do: 'Count where most good enquiries stop.', how: 'Compare the counts at each step. The biggest drop is your next priority.', owner: OWN.boss }
      ],
      measure: 'Out of every 10 good enquiries, how many become customers?', review: 'in 4 weeks',
      review_list: ['Tracker started', 'Every enquiry logged for 4 weeks', 'Biggest drop found', 'One next step picked'],
      agency: ['How many enquiries did we get last month, and from where?', 'Can you report enquiries by source, not just clicks?', 'Where do you think good enquiries are lost?'],
      evidence: ['Enquiries by source for the last 3 months', 'Form and call reports, if you have them'],
      help: 'Someone who can set up a simple tracker or customer list (CRM) and read the results with you.',
      topic: 'finding where good enquiries are lost', resource: 'R_TRACKER'
    },
    P_FOLLOWUP: {
      title: 'Reply faster and follow up every time', area: 'Enquiry follow-up',
      plain: 'Some enquiries wait too long or get missed. The first business to reply often wins the work.',
      because: 'Replies are sometimes slow, or enquiries do not move forward.',
      actions: [
        { do: 'Put every enquiry in one tracker.', how: 'One place for calls, emails, forms and messages, so none get lost.', owner: OWN.desk },
        { do: 'Reply the same business day.', how: 'Even a short note helps: thanks, when you will call, and one question.', owner: OWN.desk },
        { do: 'Follow up 3 times before you give up.', how: 'For example, on day 1, day 3 and day 7. Use the follow-up checklist.', owner: OWN.desk }
      ],
      measure: 'Out of every 10 enquiries, how many get a reply the same day?', review: 'in 2 weeks',
      review_list: ['All enquiries in one tracker', 'Same-day reply for most enquiries', '3 follow-ups before closing', 'Reply time checked each week'],
      agency: ['Where do our enquiries arrive, and who is told when one comes in?', 'Can we get an alert for every new enquiry?', 'How many enquiries did we get last month, by source?'],
      evidence: ['A list of last month’s enquiries with the time each one arrived', 'Where form and call alerts go today'],
      help: 'Someone who can set up alerts, a simple customer list (CRM) and follow-up templates.',
      topic: 'improving how you reply to and follow up on enquiries', resource: 'R_TRACKER'
    },
    P_CLOSE: {
      title: 'Turn more quotes into customers', area: 'Quotes and follow-up',
      plain: 'Good enquiries get close but do not say yes. A clear follow-up plan, and knowing why you lose, helps you win more.',
      because: 'Good enquiries do not always become customers, and quotes may not get enough follow-up.',
      actions: [
        { do: 'Follow up every quote 2 days after you send it.', how: 'Ask if they have questions and what would help them decide.', owner: OWN.sales },
        { do: 'Ask everyone who says no for the main reason.', how: 'One short question: price, timing, trust, or they picked someone else?', owner: OWN.sales },
        { do: 'Fix the most common reason.', how: 'For example, show reviews and past work, explain your price, or offer a smaller first step.', owner: OWN.boss }
      ],
      measure: 'Out of every 10 quotes, how many do you win?', review: 'in 6 weeks',
      review_list: ['Every quote followed up', 'Reason asked for every no', 'Top reason found', 'One fix made for it'],
      agency: ['Which sources bring enquiries that turn into wins, not just enquiries?', 'Can we report won work by source?', 'What proof or content would help people decide?'],
      evidence: ['Quotes sent and won by source for the last 3 months', 'Reasons you lost work, if written down'],
      help: 'Someone who can build a simple sales process: follow-up templates, a customer list (CRM) and proof like case studies.',
      topic: 'turning more of your quotes into customers', resource: 'R_TRACKER'
    },
    P_REPEAT: {
      title: 'Plan a simple follow-up so customers come back', area: 'Customer follow-up',
      plain: 'Happy customers may buy again, but only if you stay in touch and give them a reason.',
      because: 'Customers could come back, but there is little or no planned follow-up.',
      actions: function (a) {
        return [
          a.r_list === 'yes'
            ? { do: 'Sort your customer list by the date they last bought.', how: 'You will use this to send the right message at the right time.', owner: OWN.desk }
            : { do: 'Start keeping customer contact details, with their permission.', how: 'Ask at checkout or at the end of the visit: “Can we send you a reminder when it is time?”', owner: OWN.desk },
          { do: 'Pick the one best moment to remind them.', how: 'For example, when a product runs out, when a service is due, or on the same date next year.', owner: OWN.boss },
          { do: 'Send one simple message at that moment.', how: 'Say what is due, why it helps, and give one easy way to buy or book.', owner: OWN.mkt }
        ];
      },
      measure: 'Out of every 10 customers, how many buy again when they normally would?', review: 'in 8 weeks',
      review_list: ['Customer details collected with permission', 'Best reminder moment picked', 'Reminder message written and sent', 'Repeat customers counted'],
      agency: ['What messages do our customers get after they buy?', 'Can we send a reminder when a customer is due?', 'How many customers bought again last year?'],
      evidence: ['The list of automatic emails or texts customers get today', 'Repeat customers by month for the last year'],
      help: 'Someone who can set up email or text reminders and a simple customer list.',
      topic: 'bringing customers back with a simple follow-up plan', resource: 'R_REPEAT'
    },
    P_REACTIVATE: {
      title: 'Win back past customers', area: 'Winning customers back',
      plain: 'You stay in touch, but fewer customers return than you would like. A short, personal note to people who have not bought in a while often works.',
      because: 'You already follow up, so the next step is to go after customers who have gone quiet.',
      actions: [
        { do: 'Make a list of customers who have not bought in a while.', how: 'For example, no purchase or visit in 6 months.', owner: OWN.desk },
        { do: 'Send them a short, personal note.', how: 'Say you miss them, ask how things are, and give one reason to come back now.', owner: OWN.boss },
        { do: 'Ask the ones who reply why they stopped.', how: 'Their answers tell you what to fix for everyone else.', owner: OWN.boss }
      ],
      measure: 'Out of every 20 past customers you contact, how many buy again?', review: 'in 6 weeks',
      review_list: ['List of quiet customers made', 'Personal note sent', 'Reasons collected from replies', 'Customers who came back counted'],
      agency: ['How many past customers have not bought in 6 months?', 'Can we send them a personal win-back message?', 'How will we count who comes back?'],
      evidence: ['Customers with no purchase in 6 months, with contact permission', 'Results of any past win-back messages'],
      help: 'Someone who can pull a customer list and set up a win-back email or text.',
      topic: 'winning back past customers', resource: 'R_REPEAT'
    },
    P_REFERRAL: {
      title: 'Turn happy customers into reviews and referrals', area: 'Reviews and referrals',
      plain: 'Most of your customers only need you once. So the way to grow from them is reviews and word of mouth.',
      because: 'Your customers usually only need you once.',
      healthy: 'Customers already come back and you stay in touch, so reviews and referrals are the next way to grow from them.',
      actions: [
        { do: 'Ask every happy customer for a Google review.', how: 'Send the link right after the job is done, while they are happy.', owner: OWN.desk },
        { do: 'Ask them who else might need you.', how: 'Give them an easy way to share: a card, a link or a short message they can forward.', owner: OWN.desk },
        { do: 'Thank people who refer someone.', how: 'A thank-you note or a small gift. Keep it simple and honest.', owner: OWN.boss }
      ],
      measure: 'New reviews each month, and new customers who came from a referral.', review: 'in 8 weeks',
      review_list: ['Review link sent to every happy customer', 'Easy way to share set up', 'Thank-you for referrals in place', 'Reviews and referrals counted each month'],
      agency: ['How do we ask customers for reviews today?', 'Can we send the review link automatically after each job?', 'Can we track customers who came from a referral?'],
      evidence: ['Number of new reviews in the last 3 months', 'New customers who said a friend sent them'],
      help: 'Someone who can set up automatic review requests and a simple referral card or link.',
      topic: 'getting more reviews and referrals from happy customers', resource: 'R_REPEAT'
    },
    P_REPEAT_FIND: {
      title: 'Find out how many customers come back', area: 'Counting repeat customers',
      plain: 'Before you build a plan, count how many customers come back. Then you know if this is the right thing to work on.',
      because: 'You were not sure how many customers come back.',
      actions: [
        { do: 'Pull a list of customers from the last 12 months.', how: 'From your till, booking system, shop or invoices.', owner: OWN.desk },
        { do: 'Count how many bought or visited more than once.', how: 'A spreadsheet can count names that appear more than once.', owner: OWN.desk },
        { do: 'Compare it with what you would expect.', how: 'If a customer should need you every few months, most should be back by now.', owner: OWN.boss }
      ],
      measure: 'Out of every 10 customers from last year, how many came back?', review: 'in 2 weeks',
      review_list: ['Customer list pulled', 'Repeat customers counted', 'Compared with what you expect', 'Next step picked'],
      agency: ['How many of last year’s customers bought again?', 'How long do customers usually wait before buying again?', 'What do we send customers after they buy?'],
      evidence: ['Customers by number of purchases for the last 12 months'],
      help: 'Someone who can pull and count your customer data.',
      topic: 'finding out how many of your customers come back', resource: 'R_REPEAT'
    },
    P_LAUNCH_WHO: {
      title: 'Decide who your first customers are', area: 'Your first customer',
      plain: 'Before you spend on promotion, know exactly who you want first. It makes every other choice easier.',
      because: 'You cannot yet describe your first customer clearly.',
      actions: [
        { do: 'Write one sentence: we help [who] with [what] in [where].', how: 'Be specific. “Busy parents in Burlington” is better than “everyone”.', owner: OWN.boss },
        { do: 'Talk to 5 people who fit that sentence.', how: 'Ask what they use now, what annoys them about it, and what they pay.', owner: OWN.boss },
        { do: 'Change your sentence based on what you heard.', how: 'Use their words, not yours.', owner: OWN.boss }
      ],
      measure: 'You can say who it is for in one sentence, and 5 real people agree it is for them.', review: 'in 2 weeks',
      review_list: ['One-sentence customer written', '5 conversations done', 'Sentence updated'],
      agency: ['Who do you think our first customers should be, and why?', 'Where do those people spend time?', 'What would you need from us to target them?'],
      evidence: ['Notes from the 5 customer conversations'],
      help: 'Someone who can help you pick a clear first customer and test it. A marketing strategist.',
      topic: 'deciding who your first customers are', resource: 'R_LAUNCH'
    },
    P_LAUNCH_OFFER: {
      title: 'Make your offer clear', area: 'Your offer',
      plain: 'People need to know what you sell, the price, and why you are a better pick than other choices.',
      because: 'Your offer, price or reason to pick you is not clear yet.',
      actions: [
        { do: 'Write your offer in 3 lines: what it is, the price, why you.', how: 'No fancy words. Say it like you would to a friend.', owner: OWN.boss },
        { do: 'Look at 3 competitors.', how: 'Write down what they charge and what they promise.', owner: OWN.boss },
        { do: 'Test your 3 lines on 5 possible customers.', how: 'Ask them to say it back to you and tell you what is unclear.', owner: OWN.boss }
      ],
      measure: '5 out of 5 people can tell you what you sell and the price.', review: 'in 2 weeks',
      review_list: ['Offer written in 3 lines', '3 competitors checked', 'Tested on 5 people'],
      agency: ['How would you describe our offer in one line?', 'How do we compare with the main competitors?', 'What would make people pick us?'],
      evidence: ['A short competitor comparison'],
      help: 'Someone who can help shape your offer, price and message.',
      topic: 'making your offer clear before launch', resource: 'R_LAUNCH'
    },
    P_LAUNCH_ROUTE: {
      title: 'Set up an easy way to buy, book or enquire', area: 'Buying, booking or enquiring',
      plain: 'Before you promote, customers need a way to say yes that works every time.',
      because: 'Your way to buy, book or enquire is not ready or not tested.',
      actions: [
        { do: 'Choose one main way: buy online, book online, or send an enquiry.', how: 'One clear way is better than three half-ready ones.', owner: OWN.boss },
        { do: 'Set it up and ask 3 people to try it on a phone and a computer.', how: 'Watch where they get stuck. Fix it.', owner: OWN.site },
        { do: 'Make sure every order or enquiry reaches you right away.', how: 'Send a test and check the alert arrives.', owner: OWN.site }
      ],
      measure: '3 test customers finish without help.', review: 'in 1 week',
      review_list: ['One main way chosen', 'Tested by 3 people', 'Alerts tested'],
      agency: ['Has the buying, booking or enquiry form been tested on a phone?', 'Where do the alerts go?', 'What happens if it breaks?'],
      evidence: ['A screen recording of a test on a phone', 'A test alert'],
      help: 'Someone who can build or fix your website’s buy, booking or enquiry form.',
      topic: 'setting up how customers buy, book or enquire', resource: 'R_LAUNCH'
    },
    P_LAUNCH_READY: {
      title: 'Get ready to serve your first customers well', area: 'Ready to deliver',
      plain: 'Promotion only helps if you can deliver. A bad first experience is hard to undo.',
      because: 'You may not be ready to serve a rush of customers yet.',
      actions: [
        { do: 'Write down each step from order to delivery.', how: 'Who does what, and how long it takes.', owner: OWN.boss },
        { do: 'Do a practice run with a friend or family member.', how: 'Treat them like a real customer, from first contact to follow-up.', owner: OWN.boss },
        { do: 'Decide what you will do if too many orders come at once.', how: 'For example, a waitlist or a limit per day.', owner: OWN.boss }
      ],
      measure: 'A practice customer is served on time with no problems.', review: 'in 2 weeks',
      review_list: ['Steps written down', 'Practice run done', 'Plan for too many orders'],
      agency: ['How many customers could our first promotion bring?', 'Can we pause it quickly if we get too busy?'],
      evidence: ['A simple estimate of how many enquiries or orders to expect'],
      help: 'Someone who can plan a launch that matches how much you can handle.',
      topic: 'getting ready to serve your first customers', resource: 'R_LAUNCH'
    },
    P_LAUNCH_TRACK: {
      title: 'Set up a simple way to know what works', area: 'Tracking from day one',
      plain: 'From day one, write down where each customer came from. Then you know what to keep doing.',
      because: 'You do not yet have a way to know where customers come from.',
      actions: [
        { do: 'Add a “How did you hear about us?” question to your form or checkout.', how: 'Give a short list of choices plus “other”.', owner: OWN.site },
        { do: 'Set up free website stats, like Google Analytics.', how: 'Then make a test order or enquiry and check it shows up.', owner: OWN.site },
        { do: 'Start an outcome log.', how: 'One row per customer: date, where they found you, and what they spent.', owner: OWN.boss }
      ],
      measure: 'Every new customer has a source written down.', review: '2 weeks after launch',
      review_list: ['Question added to form or checkout', 'Website stats tested', 'Outcome log started'],
      agency: ['What tracking will be set up before launch?', 'Will we see enquiries or sales by source?', 'Can you show a test result?'],
      evidence: ['A screenshot of a test order or enquiry in the stats'],
      help: 'Someone who can set up website stats and test them. An analytics specialist.',
      topic: 'setting up simple tracking before launch', resource: 'R_LAUNCH'
    },
    P_LAUNCH_GO: {
      title: 'Plan a small first promotion', area: 'First promotion',
      plain: 'Your basics look ready. Start with one small, low-cost promotion and learn from it.',
      because: 'Your customer, offer, buying route, delivery and tracking all look ready.',
      actions: [
        { do: 'Pick one place your first customers already spend time.', how: 'For example, Google search, a local Facebook group, Instagram or a local event.', owner: OWN.boss },
        { do: 'Plan a 30-day test with a set budget or time limit.', how: 'Decide before you start what a good result looks like.', owner: OWN.mkt },
        { do: 'Check your outcome log each week and keep what works.', how: 'Stop what brings nothing after 30 days.', owner: OWN.boss }
      ],
      measure: 'Customers won in the first 30 days, and where they came from.', review: 'in 30 days',
      review_list: ['One place picked', '30-day test planned with a limit', 'Weekly check in the calendar'],
      agency: ['What would you do with a small 30-day budget?', 'What result should we expect?', 'How will we know it worked?'],
      evidence: ['A one-page plan for the 30-day test'],
      help: 'Someone who can run a small first promotion and report on results.',
      topic: 'planning your first promotion', resource: 'R_LAUNCH'
    },
    P_RECORD: {
      title: 'Write down every sale or enquiry, and where it came from', area: 'Recording results',
      plain: 'You cannot tell what works until each sale or enquiry is written down with where it came from. Every good report starts here.',
      because: 'Sales or enquiries, or where they came from, are not written down every time.',
      actions: [
        { do: 'Start an outcome log today.', how: 'One row per sale or enquiry: date, name, where they found you, value and result.', owner: OWN.desk },
        { do: 'Ask every new customer: “How did you find us?”', how: 'Add it to your form, checkout or phone script.', owner: OWN.desk },
        { do: 'Add up the log at the end of each month.', how: 'Count sales and money by source. That is your first real report.', owner: OWN.boss }
      ],
      measure: 'Out of every 10 new customers, how many have a source written down?', review: 'in 4 weeks',
      review_list: ['Outcome log started', 'Everyone asked how they found you', 'Month-end count done'],
      agency: ['Can your reports show sales or enquiries by source, not just clicks?', 'What tracking is set up on our website right now?', 'Have you tested it with a real order or enquiry?'],
      evidence: ['The list of tracking set up on the site', 'A sample report showing enquiries or sales by source'],
      help: 'Someone who can set up tracking and a simple results report. An analytics specialist.',
      topic: 'setting up simple tracking so you know what works', resource: 'R_MEASURE'
    },
    P_REPORTS: {
      title: 'Get reports that show real results', area: 'Clear reports',
      plain: 'Reports full of clicks and views do not tell you if marketing brings customers. Ask for reports that show enquiries, sales and cost.',
      because: 'Your reports show activity instead of results, or they do not help you decide what to do.',
      actions: function (a) {
        return [
          a.m_reports === 'no'
            ? { do: 'Pick one day each month to look at your results.', how: 'Put it in your calendar now. 30 minutes is enough to start.', owner: OWN.boss }
            : { do: 'Send the questions in your resource to whoever does your reports.', how: 'Ask for answers in writing, in plain words.', owner: OWN.boss },
          { do: 'Agree on 3 numbers for every report.', how: 'For example: new enquiries or sales, cost for each new customer, and where they came from.', owner: OWN.boss },
          { do: 'Use the one-page report template each month.', how: 'What happened, what we learned, what we will change.', owner: OWN.report }
        ];
      },
      measure: 'Each monthly report shows the 3 agreed numbers and one decision.', review: 'at your next monthly report',
      review_list: ['Questions sent', '3 numbers agreed', 'Template used for the next report', 'One decision made from it'],
      agency: ['How many enquiries or sales did marketing bring last month, and from where?', 'What did each new customer cost?', 'What will you change next month, and why?'],
      evidence: ['Last month’s enquiries or sales by source', 'Spend by channel for the same month'],
      help: 'Someone who can turn your data into a one-page report you understand. An analytics specialist.',
      topic: 'getting marketing reports that show real results', resource: 'R_AGENCY'
    }
  };

  /* Takeaways. Each one is a working file, written out in full in the download. */
  var resources = {
    R_SHOP: { name: 'Purchase-journey inspection checklist', kind: 'Checklist',
      blurb: 'Step-by-step checks from first visit to paid order, plus a place to write your numbers.',
      body: [
        ['Your numbers (last 30 days)', ['Store visits: ____', 'Product page views: ____', 'Added to cart: ____', 'Checkouts started: ____', 'Orders: ____', 'Biggest drop is between ____ and ____']],
        ['Test it on your phone', ['[ ] I found the product from Google or an ad in 3 taps or fewer', '[ ] Price, sizes and delivery time are clear on the product page', '[ ] Real reviews or customer photos are shown', '[ ] The Add to cart button is easy to see without scrolling', '[ ] Shipping cost is shown before checkout', '[ ] I can check out without making an account', '[ ] Apple Pay, Google Pay or PayPal is offered', '[ ] Checkout has 3 steps or fewer', '[ ] Each page loads in under 3 seconds', '[ ] An order confirmation email arrived']],
        ['Tracking', ['[ ] My test order shows up once in my website stats', '[ ] The order amount matches my shop', '[ ] I can see which ad or source brought the order']],
        ['What I will change first', ['____']]
      ] },
    R_BOOKING: { name: 'Booking confirmation and reminder review checklist', kind: 'Checklist',
      blurb: 'What every confirmation and reminder should say, and how to count missed visits.',
      body: [
        ['Confirmation (right after booking)', ['[ ] Sent within 5 minutes', '[ ] Date, time and how long the visit takes', '[ ] Address and parking, or the video link', '[ ] How to get ready or what to bring', '[ ] Your cancellation rule in one line', '[ ] An easy link or number to move the time']],
        ['Reminder', ['[ ] Sent 1 day before (and 2 hours before if people often forget)', '[ ] Sent by text message, not only email', '[ ] Easy way to confirm, cancel or move the time']],
        ['Booking steps', ['[ ] A new customer can book on a phone in under 2 minutes', '[ ] Open times are shown', '[ ] New customers can get in within a week, or join a waitlist']],
        ['Count each week', ['Bookings: ____  Missed: ____  Late cancels: ____  Slots refilled: ____']]
      ] },
    R_TRACKER: { name: 'Enquiry tracker and follow-up checklist', kind: 'Tracker', csv: true,
      blurb: 'A spreadsheet to log every enquiry, a follow-up checklist and three ready-to-send messages.',
      columns: ['Date', 'Name', 'Phone or email', 'Where they found us', 'Good fit? (Y/N)', 'First reply (date and time)', 'Follow-up 1', 'Follow-up 2', 'Follow-up 3', 'Call, meeting or booking? (Y/N)', 'Quote sent (date)', 'Result (Won/Lost/Open)', 'Reason if lost', 'Value', 'Notes'],
      body: [
        ['Follow-up checklist', ['[ ] Every enquiry goes in the tracker the same day', '[ ] First reply the same business day', '[ ] The reply says thanks, the next step, and asks one question', '[ ] Follow up on day 3 and day 7 if there is no answer', '[ ] After a quote, follow up 2 days later', '[ ] When someone says no, ask for the main reason', '[ ] Close every row as Won or Lost, never leave it blank', '[ ] Once a week, count: enquiries, good fits, meetings, quotes, won']],
        ['First reply', ['Hi [name], thanks for getting in touch about [need]. I can call you on [day and time], or you can pick a time here: [link]. One quick question so I can prepare: [question]']],
        ['Follow-up', ['Hi [name], just checking you saw my note about [need]. Happy to help when the time is right. Is [day] good for a quick call?']],
        ['Asking why', ['Thanks for letting me know. So we can get better, what was the main reason? Price, timing, or something else?']]
      ] },
    R_QUALIFY: { name: 'Qualification worksheet and messaging review checklist', kind: 'Worksheet',
      blurb: 'Write down your good fit and poor fit, then check your website, ads and form against it.',
      body: [
        ['Qualification worksheet', ['My best customers are (who, where, what they need): ____', 'Signs of a poor fit: ____', 'What we do not do: ____', 'Our starting price or range: ____', 'Question 1 to add to our form: ____', 'Question 2 to add to our form: ____']],
        ['Messaging review checklist', ['[ ] The first line of the homepage says who we help', '[ ] Service pages say what is included and what is not', '[ ] The area we serve, or who we serve, is clear', '[ ] A starting price or range is shown, or we say why not', '[ ] Ads and posts use the same words as the website', '[ ] The form asks 1 or 2 questions that sort good fits', '[ ] Reviews come from the kind of customer we want more of']]
      ] },
    R_REPEAT: { name: 'Repeat-purchase planning worksheet', kind: 'Worksheet',
      blurb: 'Plan when to remind customers, what to say, how to win back quiet ones, and how to ask for referrals.',
      body: [
        ['When and why they come back', ['A happy customer should need us again every: ____', 'What reminds them (refill, service due, season, new stock, birthday): ____']],
        ['How we reach them', ['[ ] Email  [ ] Text  [ ] Call  [ ] Mail', 'Do we have their permission? ____']],
        ['The reminder message', ['What is due: ____', 'Why it helps them: ____', 'One easy way to buy or book: ____']],
        ['Win back quiet customers', ['Customers with no purchase in ____ months: ____', 'Our short, personal note: ____']],
        ['If most customers only buy once', ['Review link: ____', 'How we ask for a referral: ____', 'How we say thank you: ____']],
        ['Measure', ['Out of every 10 customers, how many buy again within ____ months?', 'Today: ____   In 8 weeks: ____']]
      ] },
    R_AGENCY: { name: 'Questions for your agency and an outcome-report template', kind: 'Message and template',
      blurb: 'A ready-to-send message with five plain questions, and a one-page monthly report template.',
      body: [
        ['Message to send', ['Hi [name], I want to understand our marketing results better. Could you answer these in plain words by [date]?', '1. How many enquiries or sales did marketing bring last month, and from where?', '2. What did each new customer cost?', '3. What changed since last month, and why?', '4. What will you do differently next month?', '5. What tracking is set up, and have you tested it with a real order or enquiry?', 'Thanks, [your name]']],
        ['One-page outcome report (each month)', ['Month: ____', 'New enquiries or sales: ____', 'From ads: ____  From search: ____  From social: ____  From referrals: ____  Other: ____', 'Money spent: ____', 'Cost for each new customer: ____', 'What worked: ____', 'What did not: ____', 'One decision for next month: ____']]
      ] },
    R_MEASURE: { name: 'Simple measurement checklist and outcome log', kind: 'Tracker', csv: true,
      blurb: 'A spreadsheet to log every sale or enquiry with its source, and a short checklist.',
      columns: ['Date', 'Name', 'Type (sale, booking or enquiry)', 'Where they found us', 'Value', 'Result', 'Notes'],
      body: [
        ['Measurement checklist', ['[ ] Every sale or enquiry is written down the same day', '[ ] Every row says where they found us', '[ ] Our form or checkout asks how they found us', '[ ] Our website stats record sales or enquiries (we tested one)', '[ ] At month end, we count sales and money by source', '[ ] We write down one decision each month']]
      ] },
    R_LAUNCH: { name: 'Launch-readiness checklist', kind: 'Checklist',
      blurb: 'Everything to have in place before you spend on promotion, in the order to do it.',
      body: [
        ['Your customer', ['[ ] One sentence: we help [who] with [what] in [where]', '[ ] Talked to 5 possible customers']],
        ['Your offer', ['[ ] What it is, the price and why us, in 3 lines', '[ ] Checked 3 competitors']],
        ['A way to buy, book or enquire', ['[ ] One main way chosen', '[ ] Tested on a phone and a computer by 3 people', '[ ] Alerts reach us right away']],
        ['Ready to deliver', ['[ ] Steps from order to delivery written down', '[ ] Practice run done', '[ ] Plan for too many orders at once']],
        ['Knowing what works', ['[ ] “How did you hear about us?” question added', '[ ] Website stats record sales or enquiries', '[ ] Outcome log started']],
        ['First promotion', ['[ ] One place picked', '[ ] 30-day test with a set limit', '[ ] Weekly check in the calendar']]
      ] },
    R_REACH: { name: 'Customer source worksheet', kind: 'Worksheet',
      blurb: 'Find where your best customers come from, then plan a 30-day test to get more of them.',
      body: [
        ['Where the last 20 customers came from', ['Google search: ____  Ads: ____  Social media: ____  Referral: ____  Walk-in: ____  Other: ____']],
        ['Your best source', ['The place that brought customers who bought, paid well and were good to work with: ____']],
        ['30-day test', ['What I will do more of: ____', 'Budget or hours: ____', 'Start date: ____   Check date: ____']],
        ['Result', ['New customers from this source. Before: ____   After: ____']]
      ] }
  };

  return { shared: shared, capability: capability, paths: paths, pathFor: pathFor, priorities: priorities, resources: resources };
})();
